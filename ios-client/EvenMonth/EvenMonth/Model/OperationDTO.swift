//
//  OperationDTO.swift
//  EvenMonth
//
//  Created by Popov Alexsandr on 20.09.2026.
//

import Foundation

struct OperationsPageDTO: Decodable {
    let items: [OperationDTO]
    let total: Int
    let limit: Int
    let offset: Int
}

struct OperationDTO: Decodable, Identifiable {
    let id: Int
    let category: OperationCategory
    let status: OperationStatus
    let source: OperationSource
    let createdAt: String

    enum CodingKeys: String, CodingKey {
        case id
        case category
        case status
        case source
        case createdAt = "created_at"
    }
}

enum OperationCategory: String, Decodable {
    case transfer
    case salary
    case other
    case uncategorized
}

enum OperationStatus: String, Decodable {
    case pending
}

enum OperationSource: String, Decodable {
    case image
    case audio
}
