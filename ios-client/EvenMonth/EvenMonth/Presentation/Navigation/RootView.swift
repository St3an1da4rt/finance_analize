//
//  RootView.swift
//  EvenMonth
//
//  Created by Popov Alexsandr on 20.09.2026.
//

import SwiftUI

struct RootView: View {
    @EnvironmentObject var appState: AppState
    var body: some View {
        switch appState.phase {
        case .instruction:
            InstructionView(onAgree: appState.agreeInstruction)
        case .main:
            MainTabBar()
        }
    }
}

#Preview {
    RootView()
}
