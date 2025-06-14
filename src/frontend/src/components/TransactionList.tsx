import * as api from '../services/api';
import { FaTrash } from 'react-icons/fa';

interface TransactionListProps {
    transactions: api.Transaction[];
    onTransactionDeleted: () => void;
    loading: boolean;
}

export function TransactionList({ transactions, onTransactionDeleted, loading }: TransactionListProps) {

    const handleDelete = async (id: number) => {
        if (window.confirm('Tem certeza que deseja apagar esta transação?')) {
            try {
                await api.deleteTransaction(id);
                onTransactionDeleted();
            } catch (error) {
                alert('Falha ao apagar a transação.');
                console.error(error);
            }
        }
    };

    if (loading) {
        return <div className="text-center p-8">Carregando transações...</div>;
    }

    return (
        <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200">
            <h3 className="text-xl font-bold mb-4">Histórico de Transações</h3>
            <div className="space-y-3">
                {transactions.length === 0 && <p className="text-center text-gray-500 py-4">Nenhuma transação encontrada.</p>}
                {transactions.map(t => {
                    const amountClass = t.amount > 0 ? 'text-green-600' : 'text-red-600';
                    return (
                        <div key={t.id} className="flex justify-between items-center p-3 border-b border-gray-200 last:border-b-0">
                            <div className="flex-1">
                                <div className="font-medium">{t.description}</div>
                                <div className="text-sm text-gray-500">{new Date(t.transaction_date).toLocaleDateString('pt-BR')}</div>
                            </div>
                            <div className={`font-bold ${amountClass}`}>
                                R$ {Math.abs(t.amount).toFixed(2)}
                            </div>
                            <button onClick={() => handleDelete(t.id!)} className="text-gray-400 hover:text-red-500 ml-3">
                                <FaTrash />
                            </button>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
