import Foundation

enum APIClient {
    // # 後端基本網址，等 FastAPI 起來後改成你的網址（例：https://api.linksoouo.online）
    static let BASE_URL = URL(string: "http://127.0.0.1:8000")!

    // # 目前先用假資料模式讓畫面可測試
    static var mock: Bool = true

    static func ingest(urlString: String) async throws -> IngestItemDTO {
        if mock {
            // # 模擬後端延遲 0.5 秒
            try await Task.sleep(nanoseconds: 500_000_000)
            // # 回傳假的測試資料
            return IngestItemDTO(
                id: "mock-\(Int(Date().timeIntervalSince1970))",
                title: "範例：\(urlString.prefix(20))",
                summary: "AI 摘要（假資料）：這支影片講述了一個示範。",
                tags: ["demo", "ig", "ai"],
                created_at: ISO8601DateFormatter().string(from: Date()),
                thumb_url: nil
            )
        }

        // # 真實模式（呼叫你的後端 API）
        var req = URLRequest(url: BASE_URL.appending(path: "/ingest"))
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = try JSONEncoder().encode(IngestRequest(source_url: urlString))

        // # 使用 async/await 發送請求
        let (data, resp) = try await URLSession.shared.data(for: req)
        guard let http = resp as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
            throw URLError(.badServerResponse)
        }
        // # 將 JSON 轉成 Swift 結構
        return try JSONDecoder().decode(IngestResponse.self, from: data).item
    }
}

