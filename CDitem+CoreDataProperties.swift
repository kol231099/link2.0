import Foundation
import CoreData

extension CDItem {
    @nonobjc public class func fetchRequest() -> NSFetchRequest<CDItem> {
        NSFetchRequest<CDItem>(entityName: "CDItem")
    }

    @NSManaged public var createdAt: Date?   // 先維持和你模型一致；等會建議調整為非 Optional
    @NSManaged public var id: String?
    @NSManaged public var summary: String?
    @NSManaged public var tags: String?
    @NSManaged public var thumbURL: String?
    @NSManaged public var title: String?
}

extension CDItem: Identifiable {}

