//
//  AnaliticsView.swift
//  EvenMonth
//
//  Created by Popov Alexsandr on 20.09.2026.
//

import SwiftUI
import Foundation

struct AnalyticsView: View {
    @StateObject private var viewModel = AnalyticsViewModel()
    @State private var selectedPeriod = "20 сентября"
    private let periods = ["20 сентября", "Неделя", "Месяц", "Год"]

    let segments: [ChartSegment] = [
        .init(title: "Продукты",    amount: 20000, color: Color(red: 0.20, green: 0.20, blue: 0.75)),
        .init(title: "Развлечение", amount: 6000,  color: Color(red: 0.25, green: 0.25, blue: 0.90)),
        .init(title: "Здоровье",    amount: 6000,  color: Color(red: 0.16, green: 0.16, blue: 0.60)),
        .init(title: "Прочее",      amount: 6000,  color: Color(red: 0.13, green: 0.13, blue: 0.45)),
    ]
    
    private var total: Double { segments.reduce(0) { $0 + $1.amount } }

    private static let inputFormatter: ISO8601DateFormatter = {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return formatter
    }()

    private static let displayFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "dd.MM.yyyy HH:mm"
        return formatter
    }()

    var body: some View {
        ScrollView {
            ZStack {
                Color(red: 0.05, green: 0.05, blue: 0.08)
                    .ignoresSafeArea()
                
                VStack(alignment: .leading, spacing: 20) {
                    Text("Аналитика")
                        .font(.system(size: 28, weight: .bold))
                        .foregroundStyle(.white)
                    Menu {
                        ForEach(periods, id: \.self) { period in
                            Button(period) { selectedPeriod = period }
                        }
                    } label: {
                        HStack(spacing: 10) {
                            Text(selectedPeriod)
                                .font(.system(size: 20, weight: .medium))
                                .foregroundStyle(.white)
                            Image(systemName: "chevron.down")
                                .font(.system(size: 14, weight: .semibold))
                                .foregroundStyle(.white)
                        }
                        .padding(.horizontal, 28)
                        .padding(.vertical, 14)
                        .background(Color.white.opacity(0.06), in: Capsule())
                        .overlay(
                            Capsule().stroke(Color.white.opacity(0.2), lineWidth: 1)
                        )
                    }
                    
                    Text("\(formatAmount(total)) ₽")
                        .font(.system(size: 44, weight: .bold))
                        .foregroundStyle(.white)
                    
                    HStack {
                        Spacer()
                        DonutChart(segments: segments)
                            .frame(width: 260, height: 260)
                        Spacer()
                    }
                    
                    VStack(spacing: 14) {
                        ForEach(segments) { segment in
                            categoryRow(segment)
                        }
                    }
                }
                .padding(.horizontal, 24)
                .padding(.top, 20)
            }
        }
    }

    private func categoryRow(_ segment: ChartSegment) -> some View {
        HStack {
            Circle()
                .fill(segment.color)
                .frame(width: 14, height: 14)
            Text(segment.title)
                .font(.system(size: 17, weight: .medium))
                .foregroundStyle(.white)
            Spacer()
            Text("\(formatAmount(segment.amount))₽")
                .font(.system(size: 17, weight: .medium))
                .foregroundStyle(.white)
        }
        .padding(.horizontal, 24)
        .frame(height: 68)
        .background(
            Color(red: 0.12, green: 0.12, blue: 0.15),
            in: RoundedRectangle(cornerRadius: 34)
        )
    }

    private func formatAmount(_ value: Double) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.groupingSeparator = " "
        formatter.maximumFractionDigits = 0
        return formatter.string(from: NSNumber(value: value)) ?? "\(Int(value))"
    }
}

#Preview {
    AnalyticsView()
}

struct ChartSegment: Identifiable {
    let id = UUID()
    let title: String
    let amount: Double
    let color: Color
}

struct DonutChart: View {
    let segments: [ChartSegment]
    private let lineWidth: CGFloat = 48

    var body: some View {
        GeometryReader { geo in
            let total = segments.reduce(0) { $0 + $1.amount }
            let radius = min(geo.size.width, geo.size.height) / 2 - lineWidth / 2

            ZStack {
                ForEach(Array(segments.enumerated()), id: \.element.id) { index, segment in
                    let start = startAngle(for: index, total: total)
                    let end = endAngle(for: index, total: total)

                    Circle()
                        .trim(from: start, to: end)
                        .stroke(segment.color, style: StrokeStyle(lineWidth: lineWidth, lineCap: .butt))
                        .frame(width: radius * 2, height: radius * 2)
                        .rotationEffect(.degrees(-90)) // старт сверху
                }
            }
            .frame(width: geo.size.width, height: geo.size.height)
        }
    }

    private func fractionBefore(_ index: Int, total: Double) -> Double {
        segments.prefix(index).reduce(0) { $0 + $1.amount } / total
    }

    private func startAngle(for index: Int, total: Double) -> CGFloat {
        fractionBefore(index, total: total)
    }

    private func endAngle(for index: Int, total: Double) -> CGFloat {
        fractionBefore(index, total: total) + segments[index].amount / total
    }
}

