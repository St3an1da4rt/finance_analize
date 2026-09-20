//
//  AppCoordinator.swift
//  EvenMonth
//
//  Created by Popov Alexsandr on 20.09.2026.
//

import SwiftUI
import Combine

// MARK: - Маршруты приложения
enum AppRoute: Hashable {
    case addOperation
    case analytics
}

// MARK: - Координатор навигации
final class AppCoordinator: ObservableObject {
    @Published var path = NavigationPath()

    func navigate(to route: AppRoute) {
        path.append(route)
    }

    func pop() {
        path.removeLast()
    }

    func popToRoot() {
        path.removeLast(path.count)
    }
}
