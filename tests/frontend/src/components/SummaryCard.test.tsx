import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SummaryCard } from '../../../src/frontend/src/components/SummaryCard';

describe('SummaryCard', () => {
    const mockSummary = {
        income: 5000.00,
        expense: 2000.00,
        balance: 3000.00
    };

    test('renderiza o card de resumo corretamente', () => {
        render(<SummaryCard summary={mockSummary} />);

        expect(screen.getByText('Resumo Financeiro')).toBeInTheDocument();
        expect(screen.getByText('R$ 5.000,00')).toBeInTheDocument();
        expect(screen.getByText('R$ 2.000,00')).toBeInTheDocument();
        expect(screen.getByText('R$ 3.000,00')).toBeInTheDocument();
    });

    test('exibe valores formatados corretamente', () => {
        const summaryWithDecimals = {
            income: 1234.56,
            expense: 567.89,
            balance: 666.67
        };

        render(<SummaryCard summary={summaryWithDecimals} />);

        expect(screen.getByText('R$ 1.234,56')).toBeInTheDocument();
        expect(screen.getByText('R$ 567,89')).toBeInTheDocument();
        expect(screen.getByText('R$ 666,67')).toBeInTheDocument();
    });

    test('exibe saldo negativo corretamente', () => {
        const summaryNegative = {
            income: 1000.00,
            expense: 1500.00,
            balance: -500.00
        };

        render(<SummaryCard summary={summaryNegative} />);

        expect(screen.getByText('-R$ 500,00')).toBeInTheDocument();
    });

    test('aplica classes CSS corretas para saldo positivo', () => {
        render(<SummaryCard summary={mockSummary} />);

        const balanceElement = screen.getByText('R$ 3.000,00');
        expect(balanceElement).toHaveClass('text-green-600');
    });

    test('aplica classes CSS corretas para saldo negativo', () => {
        const summaryNegative = {
            income: 1000.00,
            expense: 1500.00,
            balance: -500.00
        };

        render(<SummaryCard summary={summaryNegative} />);

        const balanceElement = screen.getByText('-R$ 500,00');
        expect(balanceElement).toHaveClass('text-red-600');
    });

    test('renderiza com dados zerados', () => {
        const emptySummary = {
            income: 0,
            expense: 0,
            balance: 0
        };

        render(<SummaryCard summary={emptySummary} />);

        expect(screen.getByText('R$ 0,00')).toBeInTheDocument();
    });
});
