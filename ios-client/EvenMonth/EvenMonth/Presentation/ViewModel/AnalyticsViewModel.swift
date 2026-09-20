//
//  AnaliticsViewModel.swift
//  EvenMonth
//
//  Created by Popov Alexsandr on 20.09.2026.
//

import Foundation
import Combine

@MainActor
class AnalyticsViewModel: ObservableObject {
    @Published var operations: [OperationDTO] = []
    @Published var segments: [ChartSegment] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let operationsURL = URL(string: "https://parabolic-amina-unnoting.ngrok-free.dev/operations")!
    private let dataProvider: AnalyticsDataProviding

    init(dataProvider: AnalyticsDataProviding = MockAnalyticsDataProvider()) {
        self.dataProvider = dataProvider
    }

    func loadSegments() async {
        do {
            segments = try await dataProvider.expenseSegments()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func fetchOperations() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        var request = URLRequest(url: operationsURL)
        request.httpMethod = "GET"
        request.setValue("true", forHTTPHeaderField: "ngrok-skip-browser-warning")

        do {
            let (data, response) = try await dataWithRetry(for: request)

            guard let http = response as? HTTPURLResponse, (200...299).contains(http.statusCode) else {
                let status = (response as? HTTPURLResponse)?.statusCode ?? -1
                errorMessage = "Сервер вернул статус \(status)"
                return
            }

            let page = try JSONDecoder().decode(OperationsPageDTO.self, from: data)
            operations = page.items
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    private func dataWithRetry(for request: URLRequest, attempts: Int = 3) async throws -> (Data, URLResponse) {
        var lastError: Error = URLError(.unknown)

        for attempt in 1...attempts {
            do {
                return try await URLSession.shared.data(for: request)
            } catch {
                lastError = error
                let code = (error as NSError).code
                guard code == NSURLErrorCannotFindHost, attempt < attempts else { break }
                print("DNS error (attempt \(attempt)/\(attempts)), retrying...")
                try? await Task.sleep(for: .milliseconds(1500))
            }
        }

        throw lastError
    }
}
