//
//  EvenMonthApp.swift
//  EvenMonth
//
//  Created by Popov Alexsandr on 20.09.2026.
//

import SwiftUI

@main
struct EvenMonthApp: App {
    @StateObject private var coordinator = AppCoordinator()
    var body: some Scene {
        WindowGroup {
            NavigationStack(path: $coordinator.path) {
                MainTabBar()
                    .navigationDestination(for: AppRoute.self) { route in
                        switch route {
                        case .addOperation:
                            AddOperationView()
                        case .analytics:
                            AnalyticsView()
                        }
                    }
            }
            .environmentObject(coordinator)
        }
    }
}
