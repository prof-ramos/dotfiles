import AppKit
import Foundation
import CryptoKit

struct Mapping: Codable { let folder: String; let icon: String }
struct Record: Codable {
    let folder: String
    let hadCustom: Bool
    let backup: String?
    let beforeResource: String
    var expectedResource: String?
    var applied: Bool
}
struct Failure: Error, CustomStringConvertible { let description: String; init(_ s: String) { description=s } }
let fm=FileManager.default
func argument(_ name: String) -> String? {
    guard let i=CommandLine.arguments.firstIndex(of:name), i+1 < CommandLine.arguments.count else { return nil }
    return CommandLine.arguments[i+1]
}
func xattr(_ key: String,_ file: URL) throws -> String? {
    let p=Process();p.executableURL=URL(fileURLWithPath:"/usr/bin/xattr");p.arguments=["-px",key,file.path]
    let out=Pipe();p.standardOutput=out;p.standardError=FileHandle.nullDevice
    try p.run();let bytes=out.fileHandleForReading.readDataToEndOfFile();p.waitUntilExit()
    if p.terminationStatus != 0 { return nil }
    return String(decoding:bytes,as:UTF8.self).filter { !$0.isWhitespace }
}
func iconState(_ folder: URL) throws -> String {
    let finder=try xattr("com.apple.FinderInfo",folder) ?? ""
    let chars=Array(finder)
    let flags=chars.count >= 20 ? UInt16(String(chars[16..<20]),radix:16) ?? 0 : 0
    let custom=(flags & 0x0400) != 0
    let file=folder.appendingPathComponent("Icon\r")
    let resource=try xattr("com.apple.ResourceFork",file) ?? ""
    let data=(try? Data(contentsOf:file)) ?? Data()
    let hex=Array(resource)
    var bytes=[UInt8]()
    if hex.count % 2 != 0 { throw Failure("Malformed icon resource") }
    for i in stride(from:0,to:hex.count,by:2) {
        guard let byte=UInt8(String(hex[i...i+1]),radix:16) else { throw Failure("Malformed icon resource") }
        bytes.append(byte)
    }
    var digest=SHA256()
    if !bytes.isEmpty {
        guard bytes.count >= 16 else { throw Failure("Short resource header") }
        func word(_ start:Int)->Int { bytes[start..<start+4].reduce(0){($0 << 8) | Int($1)} }
        let offset=word(0);let length=word(8)
        guard offset <= bytes.count, length <= bytes.count-offset else { throw Failure("Invalid resource bounds") }
        // Resource-map runtime handles differ between folders; icon payload is stable.
        digest.update(data:Data(bytes[offset..<offset+length]))
    }
    digest.update(data:data)
    return "\(custom):"+digest.finalize().map{String(format:"%02x",$0)}.joined()
}
func safe(_ relative: String,_ root: URL) throws -> URL {
    if relative.isEmpty || relative.hasPrefix("/") || relative.split(separator:"/").contains("..") { throw Failure("Unsafe relative path") }
    let url=root.appendingPathComponent(relative).standardizedFileURL
    var cursor=url
    while cursor.path != root.path {
        if (try? cursor.resourceValues(forKeys:[.isSymbolicLinkKey]).isSymbolicLink) == true { throw Failure("Symlink in path") }
        cursor.deleteLastPathComponent()
    }
    if (try? root.resourceValues(forKeys:[.isSymbolicLinkKey]).isSymbolicLink) == true { throw Failure("Symlink root") }
    return url
}
func save(_ records: [Record],_ journal: URL) throws {
    try JSONEncoder().encode(records).write(to:journal,options:.atomic)
    try fm.setAttributes([.posixPermissions:0o600],ofItemAtPath:journal.path)
}
func run() throws {
    if let restore=argument("--restore") {
        let journal=URL(fileURLWithPath:restore)
        var records=try JSONDecoder().decode([Record].self,from:Data(contentsOf:journal))
        for i in records.indices.reversed() {
            let r=records[i];let folder=URL(fileURLWithPath:r.folder)
            let current=try iconState(folder)
            if !r.applied && current == r.beforeResource { continue }
            if current != r.expectedResource { throw Failure("Icon changed after application") }
            let image: NSImage?
            if r.hadCustom { guard let backup=r.backup, let old=NSImage(contentsOfFile:backup) else { throw Failure("Missing icon backup") };image=old } else { image=nil }
            guard NSWorkspace.shared.setIcon(image,forFile:folder.path,options:[]) else { throw Failure("Cannot restore icon") }
            records[i].applied=false;try save(records,journal)
        }
        print("Icons restored");return
    }
    guard let mapPath=argument("--map"), let homePath=argument("--home") else { throw Failure("Usage: --map PATH --home PATH [--dry-run] [--state PATH] | --restore JOURNAL") }
    let home=URL(fileURLWithPath:homePath).standardizedFileURL
    let map=URL(fileURLWithPath:mapPath).standardizedFileURL
    let mappings=try JSONDecoder().decode([Mapping].self,from:Data(contentsOf:map))
    let dry=CommandLine.arguments.contains("--dry-run")
    var jobs: [(URL,NSImage)]=[]
    for m in mappings {
        let folder=try safe(m.folder,home)
        let icon=try safe(m.icon,map.deletingLastPathComponent())
        guard let image=NSImage(contentsOf:icon),image.isValid else { throw Failure("Invalid icon: \(m.icon)") }
        jobs.append((folder,image))
    }
    if dry { print("Icon changes: \(jobs.count)");return }
    let state=URL(fileURLWithPath:argument("--state") ?? home.appendingPathComponent("Library/Application Support/dotfiles/backups").path).appendingPathComponent("icons-"+UUID().uuidString)
    var ancestor=state
    while ancestor.path != "/" {
        if (try? ancestor.resourceValues(forKeys:[.isSymbolicLinkKey]).isSymbolicLink) == true { throw Failure("Symlink in backup path") }
        ancestor.deleteLastPathComponent()
    }
    try fm.createDirectory(at:state,withIntermediateDirectories:true,attributes:[.posixPermissions:0o700])
    let journal=state.appendingPathComponent("icons.json")
    var records: [Record]=[]
    try save(records,journal)
    for (folder,image) in jobs {
        let info=try xattr("com.apple.FinderInfo",folder) ?? ""
        let chars=Array(info)
        let flags=chars.count >= 20 ? UInt16(String(chars[16..<20]),radix:16) ?? 0 : 0
        let custom=(flags & 0x0400) != 0
        var backup: String?=nil
        if custom {
            guard let data=NSWorkspace.shared.icon(forFile:folder.path).tiffRepresentation else { throw Failure("Cannot back up custom icon") }
            let dst=state.appendingPathComponent(UUID().uuidString+".tiff");try data.write(to:dst);try fm.setAttributes([.posixPermissions:0o600],ofItemAtPath:dst.path);backup=dst.path
        }
        let before=try iconState(folder)
        // Precompute intended state in a private staging folder, so recovery
        // works even if the process stops immediately after setIcon succeeds.
        let staging=state.appendingPathComponent("staging-"+UUID().uuidString)
        try fm.createDirectory(at:staging,withIntermediateDirectories:false)
        guard NSWorkspace.shared.setIcon(image,forFile:staging.path,options:[]) else { throw Failure("Cannot stage icon") }
        let intended=try iconState(staging)
        records.append(Record(folder:folder.path,hadCustom:custom,backup:backup,beforeResource:before,expectedResource:intended,applied:false));try save(records,journal)
        try fm.createDirectory(at:folder,withIntermediateDirectories:true)
        guard NSWorkspace.shared.setIcon(image,forFile:folder.path,options:[]) else { throw Failure("Cannot apply icon") }
        if try iconState(folder) != intended { throw Failure("Applied icon differs from staged recovery state") }
        records[records.count-1].applied=true;try save(records,journal)
        print("Icon applied: \(folder.path)")
    }
    print("Icons journal: \(journal.path)")
}
do { try run() } catch { fputs("\(error)\n",stderr);exit(1) }
