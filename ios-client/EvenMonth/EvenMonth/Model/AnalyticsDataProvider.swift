//
//  AnalyticsDataProvider.swift
//  EvenMonth
//
//  Created by Popov Alexsandr on 20.09.2026.
//

import SwiftUI

protocol AnalyticsDataProviding {
    func expenseSegments() async throws -> [ChartSegment]
}

struct MockAnalyticsDataProvider: AnalyticsDataProviding {
    func expenseSegments() async throws -> [ChartSegment] {
        [
            .init(title: "Продукты",    amount: 20000, color: Color(red: 0.20, green: 0.20, blue: 0.75)),
            .init(title: "Развлечение", amount: 6000,  color: Color(red: 0.25, green: 0.25, blue: 0.90)),
            .init(title: "Здоровье",    amount: 6000,  color: Color(red: 0.16, green: 0.16, blue: 0.60)),
            .init(title: "Прочее",      amount: 6000,  color: Color(red: 0.13, green: 0.13, blue: 0.45)),
        ]
    }
}
