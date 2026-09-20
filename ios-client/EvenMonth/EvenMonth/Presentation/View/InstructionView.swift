//
//  InstructionView.swift
//  EvenMonth
//
//  Created by Popov Alexsandr on 20.09.2026.
//

import SwiftUI

struct InstructionView: View {
    let onAgree: () -> Void
    var body: some View {
        VStack {
            Spacer()
            Text("Инструкция")
            Spacer()
            Button(action: onAgree) {
                Text("Ознакомлен")
            }
        }
    }
    
    private func userDef() {
        let defaults = UserDefaults.standard
        defaults.set(true, forKey: "Ознакомлен")
    }
}

//#Preview {
//    InstructionView()
//}
