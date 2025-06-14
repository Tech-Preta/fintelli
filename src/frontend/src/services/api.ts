import axios from 'axios';

// O proxy do Vite vai redirecionar as chamadas que começam com /api
const apiClient = axios.create({
    baseURL: '/api',
});

// --- Interfaces de Tipo ---
export interface Transaction {
    id?: number;
    description: string;
    amount: number;
    transaction_date: string;
}

export interface Summary {
    income: number;
    expense: number;
    balance: number;
}

// --- Funções da API ---
export const getSummary = async () => {
    const response = await apiClient.get<Summary>('/summary');
    return response.data;
};

export const getTransactions = async () => {
    const response = await apiClient.get<Transaction[]>('/transactions');
    return response.data;
};

export const addTransaction = async (transaction: Omit<Transaction, 'id'>) => {
    const response = await apiClient.post<Transaction>('/transactions', transaction);
    return response.data;
};

export const deleteTransaction = async (id: number) => {
    await apiClient.delete(`/transactions/${id}`);
};
