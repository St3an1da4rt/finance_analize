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
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let operationsURL = URL(string: "https://parabolic-amina-unnoting.ngrok-free.dev/operations")!

    func fetchOperations() async {
        isLoading = true
        errorMessage = nil

        var request = URLRequest(url: operationsURL)
        request.setValue("true", forHTTPHeaderField: "ngrok-skip-browser-warning")

        do {
            let (data, response) = try await dataWithRetry(for: request)

            guard let http = response as? HTTPURLResponse, (200...299).contains(http.statusCode) else {
                let status = (response as? HTTPURLResponse)?.statusCode ?? -1
                print("HTTP error status=\(status)")
                print("Body: \(String(data: data, encoding: .utf8) ?? "<empty>")")
                errorMessage = "Сервер вернул ошибку"
                isLoading = false
                return
            }

            let page = try JSONDecoder().decode(OperationsPageDTO.self, from: data)

            print("=== GET /operations ===")
            if let json = String(data: data, encoding: .utf8) {
                print("Raw JSON:\n\(json)")
            }
            print("total=\(page.total) limit=\(page.limit) offset=\(page.offset)")
            page.items.forEach {
                print("id=\($0.id) category=\($0.category.rawValue) source=\($0.source.rawValue) status=\($0.status.rawValue) createdAt=\($0.createdAt)")
            }

            operations = page.items
            isLoading = false
        } catch {
            print("=== fetchOperations error ===")
            print("\(error)")
            if let nsError = error as NSError? {
                print("code=\(nsError.code) domain=\(nsError.domain)")
            }
            errorMessage = error.localizedDescription
            isLoading = false
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
