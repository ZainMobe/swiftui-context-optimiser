#!/usr/bin/env bash
set -e
mkdir -p Shop/Components Shop/Features/Checkout Shop.xcodeproj
cat > Shop/Components/LoadingOverlay.swift <<'SWIFT'
import SwiftUI

struct LoadingOverlay: ViewModifier {
    let isLoading: Bool

    func body(content: Content) -> some View {
        content.overlay {
            if isLoading {
                ZStack {
                    Color.black.opacity(0.2).ignoresSafeArea()
                    ProgressView()
                }
            }
        }
    }
}

extension View {
    func loadingOverlay(_ isLoading: Bool) -> some View {
        modifier(LoadingOverlay(isLoading: isLoading))
    }
}
SWIFT
cat > Shop/Components/PriceLabel.swift <<'SWIFT'
import SwiftUI

struct PriceLabel: View {
    let amount: Decimal
    let currencyCode: String

    var body: some View {
        Text(amount, format: .currency(code: currencyCode))
            .font(.headline)
            .monospacedDigit()
    }
}
SWIFT
cat > Shop/Features/Checkout/CheckoutView.swift <<'SWIFT'
import SwiftUI

struct CheckoutView: View {
    @State private var isPaying = false

    var body: some View {
        VStack(spacing: 16) {
            PriceLabel(amount: 49.99, currencyCode: "USD")
            Button("Pay") { isPaying = true }
        }
        .padding()
    }
}
SWIFT
mkdir -p .claude
printf '# SwiftUI component index\nName | Kind | File\nLoadingOverlay | ViewModifier | Shop/Components/LoadingOverlay.swift\nPriceLabel | View | Shop/Components/PriceLabel.swift\nCheckoutView | View | Shop/Features/Checkout/CheckoutView.swift\nloadingOverlay() | View extension | Shop/Components/LoadingOverlay.swift\n' > .claude/swiftui-components.md
