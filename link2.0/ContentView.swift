import SwiftUI
import CoreData

struct ContentView: View {
    @Environment(\.managedObjectContext) private var ctx

    @FetchRequest(
        fetchRequest: {
            let req = NSFetchRequest<CDItem>(entityName: "CDItem")
            req.sortDescriptors = [NSSortDescriptor(key: "createdAt", ascending: false)]
            return req
        }(),
        animation: .default
    )
    private var items: FetchedResults<CDItem>


    // # 使用者輸入的 IG 連結
    @State private var urlString = ""
    // # 是否正在呼叫後端
    @State private var isLoading = false
    // # 顯示狀態訊息（成功或錯誤）
    @State private var status: String?

    var body: some View {
        NavigationStack {
            VStack(spacing: 12) {
                // # 文字輸入框
                TextField("貼上 IG 連結…", text: $urlString)
                    .textInputAutocapitalization(.never)
                    .keyboardType(.URL)
                    .textFieldStyle(.roundedBorder)

                // # 分析按鈕
                Button {
                    Task { await ingest() } // # 使用 async 呼叫後端
                } label: {
                    Text(isLoading ? "處理中…" : "分析這支影片")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .disabled(isLoading || URL(string: urlString) == nil) // # 無效輸入時停用按鈕

                if let status {
                    Text(status).font(.footnote).foregroundStyle(.secondary)
                }

                // # 顯示已儲存的影片摘要列表
                List {
                    ForEach(items, id: \.objectID) { item in   // ← 保險：用 Core Data 內建 objectID
                        VStack(alignment: .leading, spacing: 6) {
                            Text(item.title ?? "(無標題)").font(.headline)
                            if let summary = item.summary, !summary.isEmpty {
                                Text(summary).font(.subheadline).lineLimit(3)
                            }
                            HStack {
                                if let tags = item.tags, !tags.isEmpty {
                                    Text(tags).font(.caption2).foregroundStyle(.secondary)
                                }
                                Spacer()
                                if let date = item.createdAt {
                                    Text(date, style: .date)
                                        .font(.caption2).foregroundStyle(.secondary)
                                }
                            }
                        }
                    }
                }
            }
            .padding()
            .navigationTitle("Link 收件匣")
        }
    }

    // MARK: - 呼叫後端分析
    func ingest() async {
        guard !isLoading else { return }
        isLoading = true
        status = "送出處理中…"
        defer { isLoading = false }

        do {
            // # 呼叫 APIClient.ingest()
            let dto = try await APIClient.ingest(urlString: urlString)
            // # 儲存結果到 Core Data
            try save(dto: dto)
            status = "成功：已建立 \(dto.id)"
            urlString = ""
        } catch {
            // # 出錯時顯示訊息
            status = "失敗：\(error.localizedDescription)"
        }
    }

    // MARK: - 儲存到 Core Data
    func save(dto: IngestItemDTO) throws {
        let obj = CDItem(context: ctx)
        obj.id = dto.id
        obj.title = dto.title
        obj.summary = dto.summary
        obj.tags = (dto.tags ?? []).joined(separator: ",")
        if let s = dto.created_at, let date = ISO8601DateFormatter().date(from: s) {
            obj.createdAt = date
        } else {
            obj.createdAt = Date()
        }
        obj.thumbURL = dto.thumb_url
        try ctx.save() // # 實際寫入資料庫
    }
}

#Preview {
    ContentView()
        .environment(\.managedObjectContext, PersistenceController.shared.container.viewContext)
}

