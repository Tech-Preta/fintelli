/**
 * Testes para utilitários JavaScript do Fintelli
 */

// Utilitários de formatação de moeda
const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
};

// Utilitários de formatação de data
const formatDate = (date: string | Date): string => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return dateObj.toLocaleDateString('pt-BR');
};

// Validador de transação
const validateTransaction = (transaction: any): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];

    if (!transaction.type || !['income', 'expense'].includes(transaction.type)) {
        errors.push('Tipo de transação inválido');
    }

    if (!transaction.description || transaction.description.trim().length === 0) {
        errors.push('Descrição é obrigatória');
    }

    if (typeof transaction.amount !== 'number' || transaction.amount === 0) {
        errors.push('Valor deve ser um número diferente de zero');
    }

    if (!transaction.date || isNaN(Date.parse(transaction.date))) {
        errors.push('Data inválida');
    }

    return {
        isValid: errors.length === 0,
        errors
    };
};

// Calculadora de resumo financeiro
const calculateSummary = (transactions: any[]): { income: number; expense: number; balance: number } => {
    const summary = transactions.reduce((acc, transaction) => {
        if (transaction.type === 'income') {
            acc.income += transaction.amount;
        } else if (transaction.type === 'expense') {
            acc.expense += Math.abs(transaction.amount); // Garantir valor positivo para soma
        }
        return acc;
    }, { income: 0, expense: 0 });

    return {
        income: summary.income,
        expense: summary.expense,
        balance: summary.income - summary.expense
    };
};

describe('Utility Functions', () => {
    describe('formatCurrency', () => {
        test('deve formatar números positivos corretamente', () => {
            expect(formatCurrency(1000)).toBe('R$ 1.000,00');
            expect(formatCurrency(1234.56)).toBe('R$ 1.234,56');
            expect(formatCurrency(0.99)).toBe('R$ 0,99');
        });

        test('deve formatar números negativos corretamente', () => {
            expect(formatCurrency(-1000)).toBe('-R$ 1.000,00');
            expect(formatCurrency(-1234.56)).toBe('-R$ 1.234,56');
        });

        test('deve tratar zero corretamente', () => {
            expect(formatCurrency(0)).toBe('R$ 0,00');
        });

        test('deve tratar números decimais longos', () => {
            expect(formatCurrency(1234.5678)).toBe('R$ 1.234,57'); // Arredondamento
        });
    });

    describe('formatDate', () => {
        test('deve formatar string de data corretamente', () => {
            expect(formatDate('2024-01-15')).toBe('15/01/2024');
            expect(formatDate('2024-12-31')).toBe('31/12/2024');
        });

        test('deve formatar objeto Date corretamente', () => {
            const date = new Date('2024-01-15');
            expect(formatDate(date)).toBe('15/01/2024');
        });

        test('deve tratar datas com hora', () => {
            expect(formatDate('2024-01-15T10:30:00Z')).toBe('15/01/2024');
        });
    });

    describe('validateTransaction', () => {
        test('deve validar transação válida', () => {
            const validTransaction = {
                type: 'income',
                description: 'Salário',
                amount: 5000,
                date: '2024-01-15'
            };

            const result = validateTransaction(validTransaction);
            expect(result.isValid).toBe(true);
            expect(result.errors).toHaveLength(0);
        });

        test('deve rejeitar tipo inválido', () => {
            const invalidTransaction = {
                type: 'invalid',
                description: 'Teste',
                amount: 100,
                date: '2024-01-15'
            };

            const result = validateTransaction(invalidTransaction);
            expect(result.isValid).toBe(false);
            expect(result.errors).toContain('Tipo de transação inválido');
        });

        test('deve rejeitar descrição vazia', () => {
            const invalidTransaction = {
                type: 'income',
                description: '',
                amount: 100,
                date: '2024-01-15'
            };

            const result = validateTransaction(invalidTransaction);
            expect(result.isValid).toBe(false);
            expect(result.errors).toContain('Descrição é obrigatória');
        });

        test('deve rejeitar valor zero', () => {
            const invalidTransaction = {
                type: 'income',
                description: 'Teste',
                amount: 0,
                date: '2024-01-15'
            };

            const result = validateTransaction(invalidTransaction);
            expect(result.isValid).toBe(false);
            expect(result.errors).toContain('Valor deve ser um número diferente de zero');
        });

        test('deve rejeitar data inválida', () => {
            const invalidTransaction = {
                type: 'income',
                description: 'Teste',
                amount: 100,
                date: 'data-inválida'
            };

            const result = validateTransaction(invalidTransaction);
            expect(result.isValid).toBe(false);
            expect(result.errors).toContain('Data inválida');
        });

        test('deve retornar múltiplos erros', () => {
            const invalidTransaction = {
                type: 'invalid',
                description: '',
                amount: 0,
                date: 'invalid'
            };

            const result = validateTransaction(invalidTransaction);
            expect(result.isValid).toBe(false);
            expect(result.errors).toHaveLength(4);
        });
    });

    describe('calculateSummary', () => {
        test('deve calcular resumo corretamente com transações mistas', () => {
            const transactions = [
                { type: 'income', amount: 5000 },
                { type: 'income', amount: 1000 },
                { type: 'expense', amount: -800 },
                { type: 'expense', amount: -200 }
            ];

            const summary = calculateSummary(transactions);
            expect(summary.income).toBe(6000);
            expect(summary.expense).toBe(1000);
            expect(summary.balance).toBe(5000);
        });

        test('deve lidar com array vazio', () => {
            const summary = calculateSummary([]);
            expect(summary.income).toBe(0);
            expect(summary.expense).toBe(0);
            expect(summary.balance).toBe(0);
        });

        test('deve calcular apenas receitas', () => {
            const transactions = [
                { type: 'income', amount: 2000 },
                { type: 'income', amount: 3000 }
            ];

            const summary = calculateSummary(transactions);
            expect(summary.income).toBe(5000);
            expect(summary.expense).toBe(0);
            expect(summary.balance).toBe(5000);
        });

        test('deve calcular apenas despesas', () => {
            const transactions = [
                { type: 'expense', amount: -1000 },
                { type: 'expense', amount: -500 }
            ];

            const summary = calculateSummary(transactions);
            expect(summary.income).toBe(0);
            expect(summary.expense).toBe(1500);
            expect(summary.balance).toBe(-1500);
        });

        test('deve tratar valores decimais corretamente', () => {
            const transactions = [
                { type: 'income', amount: 1234.56 },
                { type: 'expense', amount: -567.89 }
            ];

            const summary = calculateSummary(transactions);
            expect(summary.income).toBe(1234.56);
            expect(summary.expense).toBe(567.89);
            expect(summary.balance).toBeCloseTo(666.67, 2);
        });
    });
});

describe('Browser Compatibility', () => {
    test('deve suportar APIs modernas do JavaScript', () => {
        // Testa se APIs modernas estão disponíveis
        expect(typeof Promise).toBe('function');
        expect(typeof fetch).toBe('function');
        expect(typeof URLSearchParams).toBe('function');
        expect(typeof Date.prototype.toISOString).toBe('function');
    });

    test('deve suportar funcionalidades ES6+', () => {
        // Testa arrow functions
        const arrowFunction = () => 'test';
        expect(arrowFunction()).toBe('test');

        // Testa template literals
        const name = 'Fintelli';
        expect(`Hello ${name}`).toBe('Hello Fintelli');

        // Testa destructuring
        const obj = { a: 1, b: 2 };
        const { a, b } = obj;
        expect(a).toBe(1);
        expect(b).toBe(2);

        // Testa spread operator
        const arr1 = [1, 2];
        const arr2 = [...arr1, 3];
        expect(arr2).toEqual([1, 2, 3]);
    });
});

describe('Error Handling', () => {
    test('deve tratar erros graciosamente', () => {
        const errorFunction = () => {
            throw new Error('Erro de teste');
        };

        expect(() => errorFunction()).toThrow('Erro de teste');
    });

    test('deve validar tipos de entrada', () => {
        // Testa se função lida com tipos inesperados
        expect(() => formatCurrency('not a number' as any)).toThrow();
    });
});
