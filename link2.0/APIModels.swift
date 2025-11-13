import Foundation

// # App 傳給後端的請求格式
struct IngestRequest: Codable {
    let source_url: String
}

// # 後端回傳的影片資訊格式
struct IngestItemDTO: Codable {
    let id: String
    let title: String?
    let summary: String?
    let tags: [String]?
    let created_at: String?
    let thumb_url: String?
}

// # 整體回傳包裝（後端會回一個 item）
struct IngestResponse: Codable {
    let item: IngestItemDTO
}

