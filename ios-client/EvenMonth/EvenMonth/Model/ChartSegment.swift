//
//  ChartSegment.swift
//  EvenMonth
//
//  Created by Popov Alexsandr on 20.09.2026.
//

import SwiftUI

struct ChartSegment: Identifiable {
    let id = UUID()
    let title: String
    let amount: Double
    let color: Color
}
