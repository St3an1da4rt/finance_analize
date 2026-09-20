//
//  AppOperationViewModel.swift
//  EvenMonth
//
//  Created by Popov Alexsandr on 20.09.2026.
//

import SwiftUI
import PhotosUI
import Combine

@MainActor
final class AddOperationViewModel: ObservableObject {
    // MARK: - Published
    @Published var item: PhotosPickerItem?
    @Published var image: UIImage?
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var showError: Bool = false
    
    var onLoadingFinished: (() -> Void)?
    
    func upload(image: UIImage) {
        guard let jpegData = image.jpegData(compressionQuality: 0.8) else {
            errorMessage = "Не удалось преобразовать изображение"
            return
        }

        isLoading = true
        errorMessage = nil

        var request = URLRequest(url: URL(string: "https://parabolic-amina-unnoting.ngrok-free.dev/images")!)
        request.httpMethod = "POST"

        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"photo.jpg\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
        body.append(jpegData)
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
        request.httpBody = body

        URLSession.shared.dataTask(with: request) { [weak self] _, response, error in
            DispatchQueue.main.async {
                guard let self else { return }
                self.isLoading = false
                if let error {
                    self.errorMessage = error.localizedDescription
                } else if let http = response as? HTTPURLResponse, !(200...299).contains(http.statusCode) {
                    self.errorMessage = "Сервер вернул статус \(http.statusCode)"
                } else {
                    self.onLoadingFinished?()
                }
            }
        }.resume()
    }
}
