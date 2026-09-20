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

    private let url = URL(string: "https://parabolic-amina-unnoting.ngrok-free.dev/operations")!

    func fetchOperations() async throws -> OperationsPageDTO {
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("true", forHTTPHeaderField: "ngrok-skip-browser-warning")

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let http = response as? HTTPURLResponse, (200...299).contains(http.statusCode) else {
            let status = (response as? HTTPURLResponse)?.statusCode ?? -1
            throw NSError(domain: "OperationsService", code: status,
                          userInfo: [NSLocalizedDescriptionKey: "Сервер вернул статус \(status)"])
        }
        
        return try JSONDecoder().decode(OperationsPageDTO.self, from: data)
    }
}
