import SwiftUI
import CoreData
@main
struct link2_0App: App {
    let persistence = PersistenceController.shared // # 建立 PersistenceController 實例

    var body: some Scene {
        WindowGroup {
            ContentView()
                // # 把 Core Data 的 Context 注入整個 App 的環境
                .environment(\.managedObjectContext, persistence.container.viewContext)
        }
    }
}

