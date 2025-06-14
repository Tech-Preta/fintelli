import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TransactionForm } from '../../../src/frontend/src/components/TransactionForm';
import * as api from '../../../src/frontend/src/services/api';

// Mock da API
jest.mock('../../../src/frontend/src/services/api');
const mockApi = api as jest.Mocked<typeof api>;

describe('TransactionForm', () => {
    const mockOnTransactionAdded = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('renderiza o formulário corretamente', () => {
        render(<TransactionForm onTransactionAdded={mockOnTransactionAdded} />);

        expect(screen.getByText('Adicionar Lançamento')).toBeInTheDocument();
        expect(screen.getByLabelText(/tipo/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/descrição/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/valor/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/data/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /adicionar lançamento/i })).toBeInTheDocument();
    });

    test('campos têm valores padrão corretos', () => {
        render(<TransactionForm onTransactionAdded={mockOnTransactionAdded} />);

        const typeSelect = screen.getByLabelText(/tipo/i) as HTMLSelectElement;
        const dateInput = screen.getByLabelText(/data/i) as HTMLInputElement;

        expect(typeSelect.value).toBe('income');
        expect(dateInput.value).toBe(new Date().toISOString().split('T')[0]);
    });

    test('permite alteração de valores dos campos', async () => {
        const user = userEvent.setup();
        render(<TransactionForm onTransactionAdded={mockOnTransactionAdded} />);

        const descriptionInput = screen.getByLabelText(/descrição/i);
        const amountInput = screen.getByLabelText(/valor/i);
        const typeSelect = screen.getByLabelText(/tipo/i);

        await user.type(descriptionInput, 'Salário');
        await user.type(amountInput, '5000');
        await user.selectOptions(typeSelect, 'expense');

        expect(descriptionInput).toHaveValue('Salário');
        expect(amountInput).toHaveValue(5000);
        expect(typeSelect).toHaveValue('expense');
    });

    test('submete formulário com dados corretos para receita', async () => {
        const user = userEvent.setup();
        mockApi.addTransaction.mockResolvedValue({
            id: 1,
            description: 'Salário',
            amount: 5000,
            transaction_date: '2024-06-14'
        });

        render(<TransactionForm onTransactionAdded={mockOnTransactionAdded} />);

        await user.type(screen.getByLabelText(/descrição/i), 'Salário');
        await user.type(screen.getByLabelText(/valor/i), '5000');
        await user.click(screen.getByRole('button', { name: /adicionar lançamento/i }));

        await waitFor(() => {
            expect(mockApi.addTransaction).toHaveBeenCalledWith({
                description: 'Salário',
                amount: 5000,
                transaction_date: expect.any(String)
            });
        });

        expect(mockOnTransactionAdded).toHaveBeenCalled();
    });

    test('submete formulário com dados corretos para despesa', async () => {
        const user = userEvent.setup();
        mockApi.addTransaction.mockResolvedValue({
            id: 2,
            description: 'Mercado',
            amount: -300,
            transaction_date: '2024-06-14'
        });

        render(<TransactionForm onTransactionAdded={mockOnTransactionAdded} />);

        await user.selectOptions(screen.getByLabelText(/tipo/i), 'expense');
        await user.type(screen.getByLabelText(/descrição/i), 'Mercado');
        await user.type(screen.getByLabelText(/valor/i), '300');
        await user.click(screen.getByRole('button', { name: /adicionar lançamento/i }));

        await waitFor(() => {
            expect(mockApi.addTransaction).toHaveBeenCalledWith({
                description: 'Mercado',
                amount: -300, // Deve ser negativo para despesa
                transaction_date: expect.any(String)
            });
        });
    });

    test('não submete formulário com campos vazios', async () => {
        const user = userEvent.setup();
        render(<TransactionForm onTransactionAdded={mockOnTransactionAdded} />);

        await user.click(screen.getByRole('button', { name: /adicionar lançamento/i }));

        expect(mockApi.addTransaction).not.toHaveBeenCalled();
        expect(mockOnTransactionAdded).not.toHaveBeenCalled();
    });

    test('mostra estado de loading durante submissão', async () => {
        const user = userEvent.setup();
        // Simula demora na API
        mockApi.addTransaction.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

        render(<TransactionForm onTransactionAdded={mockOnTransactionAdded} />);

        await user.type(screen.getByLabelText(/descrição/i), 'Teste');
        await user.type(screen.getByLabelText(/valor/i), '100');

        const submitButton = screen.getByRole('button', { name: /adicionar lançamento/i });
        await user.click(submitButton);

        expect(screen.getByText(/adicionando.../i)).toBeInTheDocument();
        expect(submitButton).toBeDisabled();
    });

    test('limpa formulário após submissão bem-sucedida', async () => {
        const user = userEvent.setup();
        mockApi.addTransaction.mockResolvedValue({
            id: 3,
            description: 'Teste',
            amount: 100,
            transaction_date: '2024-06-14'
        });

        render(<TransactionForm onTransactionAdded={mockOnTransactionAdded} />);

        const descriptionInput = screen.getByLabelText(/descrição/i);
        const amountInput = screen.getByLabelText(/valor/i);

        await user.type(descriptionInput, 'Teste');
        await user.type(amountInput, '100');
        await user.click(screen.getByRole('button', { name: /adicionar lançamento/i }));

        await waitFor(() => {
            expect(descriptionInput).toHaveValue('');
            expect(amountInput).toHaveValue(null);
        });
    });
});
