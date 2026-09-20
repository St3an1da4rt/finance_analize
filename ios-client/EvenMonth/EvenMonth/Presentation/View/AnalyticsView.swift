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
    @State private var selectedDate = Date()

    private var total: Double { viewModel.segments.reduce(0) { $0 + $1.amount } }

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
                    DatePicker(
                        "",
                        selection: $selectedDate,
                        displayedComponents: .date
                    )
                    .labelsHidden()
                    .datePickerStyle(.compact)
                    .tint(Color(red: 0.24, green: 0.24, blue: 0.75))
                    .environment(\.colorScheme, .dark)

                    Text("\(formatAmount(total)) ₽")
                        .font(.system(size: 44, weight: .bold))
                        .foregroundStyle(.white)

                    HStack {
                        Spacer()
                        DonutChart(segments: viewModel.segments)
                            .frame(width: 260, height: 260)
                        Spacer()
                    }

                    VStack(spacing: 14) {
                        ForEach(viewModel.segments) { segment in
                            categoryRow(segment)
                        }
                    }
                }
                .padding(.horizontal, 24)
                .padding(.top, 20)
            }
        }
        .task {
            await viewModel.loadSegments()
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
                        .rotationEffect(.degrees(-90))
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

