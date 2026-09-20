//
//  MainTabBar.swift
//  EvenMonth
//
//  Created by Popov Alexsandr on 20.09.2026.
//

import SwiftUI

struct MainTabBar: View {
    @State private var selectedTab = 1

    var body: some View {
        VStack {
            content
            Spacer()
            HStack(spacing: 8) {
                tabButton(icon: "chart.bar", tag: 0)
                tabButton(icon: "message", tag: 1)
            }
            .padding(6)
            .background(
                Color(red: 0.09, green: 0.09, blue: 0.15),
                in: RoundedRectangle(cornerRadius: 28)
            )
            .padding(.horizontal, 16)
            .padding(.bottom, 20)
        }
        .background(Color(red: 0.05, green: 0.05, blue: 0.08))
    }

    @ViewBuilder
    private var content: some View {
        switch selectedTab {
        case 0:
            AnalyticsView()
        default:
            AddOperationView()
        }
    }

    private func tabButton(icon: String, tag: Int) -> some View {
        Button {
            withAnimation(.spring(response: 0.3)) {
                selectedTab = tag
            }
        } label: {
            Image(systemName: icon)
                .font(.system(size: 20))
                .foregroundStyle(.white)
                .frame(maxWidth: .infinity)
                .frame(height: 48)
                .background(
                    selectedTab == tag ? Color(red: 0.24, green: 0.24, blue: 0.75) : Color.clear,
                    in: Capsule()
                )
        }
        .buttonStyle(.plain)
    }
}

#Preview {
    MainTabBar()
}
