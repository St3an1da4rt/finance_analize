//
//  AppState().swift
//  EvenMonth
//
//  Created by Popov Alexsandr on 20.09.2026.
//

import Foundation
import Combine

final class AppState: ObservableObject {
    enum Phase {
        case instruction
        case main
    }
    
    @Published var phase: Phase
    
    init() {
        let agree = UserDefaults.standard.bool(forKey: "Instruction")
        self.phase = agree ? .main : .instruction
    }
    
    func agreeInstruction() {
        UserDefaults.standard.set(true, forKey: "Instruction")
        self.phase = .main
    }
}

