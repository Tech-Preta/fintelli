import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TransactionList } from '../../../src/frontend/src/components/TransactionList';

const mockTransactions = [
    {
        id: 1,
        type: 'income',
        description: 'Salário',
        amount: 5000.00,
        date: '2024-01-15',
        created_at: '2024-01-15T10:00:00Z'
    },
    {
        id: 2,
        type: 'expense',
        description: 'Supermercado',
        amount: -150.00,
        date: '2024-01-14',
        created_at: '2024-01-14T15:30:00Z'
    },
    {
        id: 3,
        type: 'expense',
        description: 'Gasolina',
        amount: -80.00,
        date: '2024-01-13',
        created_at: '2024-01-13T08:45:00Z'
    }
];

describe('TransactionList', () => {
    const mockOnTransactionDeleted = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('renderiza a lista de transações corretamente', () => {
        render(
            <TransactionList
                transactions={mockTransactions}
                onTransactionDeleted={mockOnTransactionDeleted}
            />
        );

        expect(screen.getByText('Últimas Transações')).toBeInTheDocument();
        expect(screen.getByText('Salário')).toBeInTheDocument();
        expect(screen.getByText('Supermercado')).toBeInTheDocument();
        expect(screen.getByText('Gasolina')).toBeInTheDocument();
    });

    test('exibe mensagem quando não há transações', () => {
        render(
            <TransactionList
                transactions={[]}
                onTransactionDeleted={mockOnTransactionDeleted}
            />
        );

        expect(screen.getByText('Nenhuma transação encontrada')).toBeInTheDocument();
    });

    test('formata valores monetários corretamente', () => {
        render(
            <TransactionList
                transactions={mockTransactions}
                onTransactionDeleted={mockOnTransactionDeleted}
            />
        );

        expect(screen.getByText('R$ 5.000,00')).toBeInTheDocument();
        expect(screen.getByText('-R$ 150,00')).toBeInTheDocument();
        expect(screen.getByText('-R$ 80,00')).toBeInTheDocument();
    });

    test('formata datas corretamente', () => {
        render(
            <TransactionList
                transactions={mockTransactions}
                onTransactionDeleted={mockOnTransactionDeleted}
            />
        );

        expect(screen.getByText('15/01/2024')).toBeInTheDocument();
        expect(screen.getByText('14/01/2024')).toBeInTheDocument();
        expect(screen.getByText('13/01/2024')).toBeInTheDocument();
    });

    test('aplica classes CSS corretas para receitas', () => {
        render(
            <TransactionList
                transactions={mockTransactions}
                onTransactionDeleted={mockOnTransactionDeleted}
            />
        );

        const incomeAmount = screen.getByText('R$ 5.000,00');
        expect(incomeAmount.closest('.transaction-item')).toHaveClass('border-green-200');
    });

    test('aplica classes CSS corretas para despesas', () => {
        render(
            <TransactionList
                transactions={mockTransactions}
                onTransactionDeleted={mockOnTransactionDeleted}
            />
        );

        const expenseAmount = screen.getByText('-R$ 150,00');
        expect(expenseAmount.closest('.transaction-item')).toHaveClass('border-red-200');
    });

    test('exibe botões de deletar para cada transação', () => {
        render(
            <TransactionList
                transactions={mockTransactions}
                onTransactionDeleted={mockOnTransactionDeleted}
            />
        );

        const deleteButtons = screen.getAllByRole('button', { name: /deletar/i });
        expect(deleteButtons).toHaveLength(3);
    });

    test('chama callback de deletar quando botão é clicado', async () => {
        const user = userEvent.setup();

        render(
            <TransactionList
                transactions={mockTransactions}
                onTransactionDeleted={mockOnTransactionDeleted}
            />
        );

        const deleteButtons = screen.getAllByRole('button', { name: /deletar/i });
        await user.click(deleteButtons[0]);

        expect(mockOnTransactionDeleted).toHaveBeenCalledWith(1);
    });

    test('ordena transações por data (mais recente primeiro)', () => {
        const unorderedTransactions = [
            { ...mockTransactions[2], date: '2024-01-13' },
            { ...mockTransactions[0], date: '2024-01-15' },
            { ...mockTransactions[1], date: '2024-01-14' }
        ];

        render(
            <TransactionList
                transactions={unorderedTransactions}
                onTransactionDeleted={mockOnTransactionDeleted}
            />
        );

        const transactionElements = screen.getAllByRole('listitem');

        // Verifica se a primeira transação é a mais recente (15/01)
        expect(transactionElements[0]).toHaveTextContent('15/01/2024');
        // Verifica se a última transação é a mais antiga (13/01)
        expect(transactionElements[2]).toHaveTextContent('13/01/2024');
    });

    test('trata transações com valores decimais', () => {
        const decimalTransactions = [
            {
                id: 4,
                type: 'income',
                description: 'Freelance',
                amount: 1234.56,
                date: '2024-01-10',
                created_at: '2024-01-10T12:00:00Z'
            }
        ];

        render(
            <TransactionList
                transactions={decimalTransactions}
                onTransactionDeleted={mockOnTransactionDeleted}
            />
        );

        expect(screen.getByText('R$ 1.234,56')).toBeInTheDocument();
    });
});
