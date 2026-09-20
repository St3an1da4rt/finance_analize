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
    @State private var selectedPeriod = "Неделю"
    private let periods = ["День", "Неделю", "Месяц", "Год"]

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
        ZStack {
            Color(red: 0.05, green: 0.05, blue: 0.08)
                .ignoresSafeArea()

            VStack(spacing: 24) {
                HStack(spacing: 16) {
                    Text("Аналитика за")
                        .font(.system(size: 22, weight: .bold))
                        .foregroundStyle(.white)

                    Menu {
                        ForEach(periods, id: \.self) { period in
                            Button(period) {
                                selectedPeriod = period
                            }
                        }
                    } label: {
                        HStack(spacing: 6) {
                            Text(selectedPeriod)
                                .font(.system(size: 17, weight: .medium))
                            Image(systemName: "chevron.down")
                                .font(.system(size: 13, weight: .semibold))
                        }
                        .foregroundStyle(.white)
                    }

                    Spacer()
                }
                HStack(spacing: 12) {
                    statCard(title: "Расходы", progress: 0.7)
                    statCard(title: "Доходы", progress: 0.45)
                }

                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(viewModel.operations) { operation in
                            operationRow(operation)
                        }
                    }
                }
            }
            .padding(.horizontal, 24)
            .padding(.top, 16)
        }
        .task {
            await viewModel.fetchOperations()
        }
    }

    private func operationRow(_ operation: OperationDTO) -> some View {
        HStack(spacing: 12) {
            Image(systemName: operation.source == .image ? "photo" : "waveform")
                .font(.system(size: 18))
                .foregroundStyle(.white)
                .frame(width: 40, height: 40)
                .background(
                    Color(red: 0.24, green: 0.24, blue: 0.75),
                    in: RoundedRectangle(cornerRadius: 12)
                )

            VStack(alignment: .leading, spacing: 4) {
                Text(operation.category.rawValue)
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundStyle(.white)
                Text(formattedDate(operation.createdAt))
                    .font(.system(size: 13))
                    .foregroundStyle(.white.opacity(0.6))
            }

            Spacer()

            Text(operation.source.rawValue)
                .font(.system(size: 13))
                .foregroundStyle(.white.opacity(0.6))
        }
        .padding(16)
        .background(
            Color(red: 0.12, green: 0.12, blue: 0.15),
            in: RoundedRectangle(cornerRadius: 20)
        )
    }

    private func formattedDate(_ raw: String) -> String {
        guard let date = Self.inputFormatter.date(from: raw) else { return raw }
        return Self.displayFormatter.string(from: date)
    }

    private func statCard(title: String, progress: CGFloat) -> some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(title)
                .font(.system(size: 16, weight: .semibold))
                .foregroundStyle(.white)

            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    Capsule()
                        .fill(Color.white.opacity(0.15))
                    Capsule()
                        .fill(Color.white.opacity(0.85))
                        .frame(width: geo.size.width * progress)
                }
            }
            .frame(height: 10)
        }
        .padding(16)
        .frame(maxWidth: .infinity, minHeight: 90)
        .background(
            Color(red: 0.12, green: 0.12, blue: 0.15),
            in: RoundedRectangle(cornerRadius: 20)
        )
    }
}

#Preview {
    AnalyticsView()
}

