//
//  HomeView.swift
//  EvenMonth
//
//  Created by Popov Alexsandr on 20.09.2026.
//

import SwiftUI
import PhotosUI

struct AddOperationView: View {
    @EnvironmentObject private var coordinator: AppCoordinator
    @StateObject private var viewModel = AddOperationViewModel()
    @State private var item: PhotosPickerItem?
    @State private var image: UIImage?

    var body: some View {
        ZStack {
            Color(red: 0.05, green: 0.05, blue: 0.08)
                .ignoresSafeArea()

            VStack(spacing: 16) {
                PhotosPicker(selection: $item, matching: .images) {
                    VStack(spacing: 12) {
                        Image(systemName: "camera")
                            .font(.system(size: 56))
                        Text("Фото")
                            .font(.system(size: 18, weight: .semibold))
                    }
                    .foregroundStyle(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: 220)
                    .background(
                        Color(red: 0.24, green: 0.24, blue: 0.85),
                        in: RoundedRectangle(cornerRadius: 44)
                    )
                }
                .onChange(of: item) { _, newItem in
                    Task {
                        if let data = try? await newItem?.loadTransferable(type: Data.self),
                           let uiImage = UIImage(data: data) {
                            viewModel.upload(image: uiImage)
                        }
                    }
                }

                .buttonStyle(.plain)

                Text("или")
                    .foregroundStyle(.white)
                    .font(.system(size: 15, weight: .medium))
                    .padding(.vertical, 4)

                Button {
                    //
                } label: {
                    VStack(spacing: 16) {
                        HStack(spacing: 10) {
                            waveBar(height: 32, delay: 0.0)
                            waveBar(height: 52, delay: 0.15)
                            waveBar(height: 68, delay: 0.3)
                            waveBar(height: 52, delay: 0.45)
                            waveBar(height: 32, delay: 0.6)
                        }
                        Text("Голосовой ввод")
                            .font(.system(size: 18, weight: .semibold))
                    }
                    .foregroundStyle(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: 220)
                    .background(
                        Color(red: 0.13, green: 0.13, blue: 0.16),
                        in: RoundedRectangle(cornerRadius: 44)
                    )
                }
                .buttonStyle(.plain)
            }
            .padding(.horizontal, 28)
        }
    }

    private func waveBar(height: CGFloat, delay: Double) -> some View {
        Capsule()
            .fill(Color.white)
            .frame(width: 12, height: height)
    }
}

#Preview {
    AddOperationView()
}
