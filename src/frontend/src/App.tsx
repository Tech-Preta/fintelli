import { useState, useEffect } from 'react';
import { getSummary, getTransactions, Transaction, Summary } from './services/api';
import { TransactionForm } from './components/TransactionForm';
import { TransactionList } from './components/TransactionList';
import { SummaryCard } from './components/SummaryCard';

function App() {
    const [summary, setSummary] = useState<Summary>({ income: 0, expense: 0, balance: 0 });
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        // Função para buscar todos os dados iniciais
        const fetchData = async () => {
            try {
                setLoading(true);
                const summaryRes = await getSummary();
                const transactionsRes = await getTransactions();
                setSummary(summaryRes);
                setTransactions(transactionsRes);
            } catch (error) {
                console.error("Failed to fetch data", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const refreshData = async () => {
        try {
            const summaryRes = await getSummary();
            const transactionsRes = await getTransactions();
            setSummary(summaryRes);
            setTransactions(transactionsRes);
        } catch (error) {
            console.error("Failed to fetch data", error);
        }
    };

    return (
        <div className="container mx-auto p-8">
            <h1 className="text-4xl font-bold text-center mb-8">🧠 Fintelli - Finanças Inteligentes com IA</h1>

            {/* Cards de Resumo */}
            <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <SummaryCard
                    title="Total de Receitas"
                    value={summary.income}
                    color="green"
                    icon={<span>📈</span>}
                />
                <SummaryCard
                    title="Total de Despesas"
                    value={summary.expense}
                    color="red"
                    icon={<span>📉</span>}
                />
                <SummaryCard
                    title="Saldo Atual"
                    value={summary.balance}
                    color="blue"
                    icon={<span>💰</span>}
                />
            </section>

            {/* Formulário de Nova Transação */}
            <section className="mb-8">
                <TransactionForm onTransactionAdded={refreshData} />
            </section>

            {/* Lista de Transações */}
            <section>
                <TransactionList transactions={transactions} onTransactionDeleted={refreshData} loading={loading} />
            </section>
        </div>
    );
}

export default App;
