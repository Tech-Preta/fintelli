import React, { useState } from 'react';
import * as api from '../services/api';

interface TransactionFormProps {
    onTransactionAdded: () => void;
}

export function TransactionForm({ onTransactionAdded }: TransactionFormProps) {
    const [description, setDescription] = useState('');
    const [amount, setAmount] = useState('');
    const [type, setType] = useState<'income' | 'expense'>('income');
    const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
    const [isSubmitting, setIsSubmitting] = useState(false);

    console.log('TransactionForm mounted', { description, amount, type, date });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        console.log('Form submitted', { description, amount, date, type });

        if (!description || !amount || !date) {
            console.log('Validation failed', { description, amount, date });
            return;
        }

        setIsSubmitting(true);
        const numericAmount = parseFloat(amount);
        const finalAmount = type === 'expense' ? -Math.abs(numericAmount) : Math.abs(numericAmount);

        console.log('Sending transaction', { description, amount: finalAmount, transaction_date: date });

        try {
            const result = await api.addTransaction({
                description,
                amount: finalAmount,
                transaction_date: date,
            });

            console.log('Transaction added successfully', result);

            // Limpa o formulário
            setDescription('');
            setAmount('');
            setType('income');
            setDate(new Date().toISOString().split('T')[0]);

            // Notifica o componente pai
            onTransactionAdded();
        } catch (error) {
            console.error("Erro ao adicionar transação", error);
            alert("Não foi possível adicionar a transação. Tente novamente.");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200">
            <h3 className="text-xl font-bold mb-4">Adicionar Lançamento</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Tipo
                    </label>
                    <select
                        value={type}
                        onChange={(e) => setType(e.target.value as 'income' | 'expense')}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="income">Receita</option>
                        <option value="expense">Despesa</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Descrição
                    </label>
                    <input
                        type="text"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Digite a descrição..."
                        className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Valor
                    </label>
                    <input
                        type="number"
                        step="0.01"
                        value={amount}
                        onChange={(e) => setAmount(e.target.value)}
                        placeholder="0,00"
                        className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Data
                    </label>
                    <input
                        type="date"
                        value={date}
                        onChange={(e) => setDate(e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                    />
                </div>

                <button
                    type="submit"
                    disabled={isSubmitting}
                    onClick={() => console.log('Button clicked!')}
                    className="w-full bg-blue-600 text-white font-bold py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                >
                    {isSubmitting ? 'Adicionando...' : 'Adicionar Lançamento'}
                </button>
            </form>
        </div>
    );
}
