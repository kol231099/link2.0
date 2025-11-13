import CoreData

final class PersistenceController {
    static let shared = PersistenceController()

    let container: NSPersistentContainer

    init(inMemory: Bool = false) {
        // ⬇️ 名稱要和 .xcdatamodeld 完全相同（大小寫也要一致）
        container = NSPersistentContainer(name: "LinkModel")

        if inMemory {
            container.persistentStoreDescriptions.first?.url = URL(fileURLWithPath: "/dev/null")
        }

        // ✅ 開啟輕量遷移
        if let desc = container.persistentStoreDescriptions.first {
            desc.shouldMigrateStoreAutomatically = true
            desc.shouldInferMappingModelAutomatically = true
        }

        container.loadPersistentStores { [weak self] storeDescription, error in
            if let error = error as NSError? {
                print("❌ Core Data load failed: \(error), \(error.userInfo)")

                // 🔁 常見的遷移/建表衝突（像 'table ZCDITEM already exists'）→ 刪庫重建
                if let url = storeDescription.url {
                    do {
                        try self?.nukeStoreFiles(at: url)
                        // 再嘗試一次
                        self?.container.loadPersistentStores { _, err2 in
                            if let err2 = err2 {
                                fatalError("🚨 Reload persistent store failed: \(err2)")
                            } else {
                                print("✅ Recreated store successfully at \(url)")
                            }
                        }
                    } catch {
                        fatalError("🚨 Could not delete old store: \(error)")
                    }
                } else {
                    fatalError("🚨 Persistent store has no URL")
                }
            } else {
                print("✅ Core Data store loaded: \(storeDescription)")
            }
        }

        container.viewContext.automaticallyMergesChangesFromParent = true
        container.viewContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
    }

    /// 刪除 sqlite / -shm / -wal 三件組
    private func nukeStoreFiles(at sqliteURL: URL) throws {
        let fm = FileManager.default
        let shm = sqliteURL.deletingPathExtension().appendingPathExtension("sqlite-shm")
        let wal = sqliteURL.deletingPathExtension().appendingPathExtension("sqlite-wal")
        for url in [sqliteURL, shm, wal] {
            if fm.fileExists(atPath: url.path) {
                try fm.removeItem(at: url)
            }
        }
    }
}



