import React from 'react';

interface SummaryCardProps {
    title: string;
    value: number;
    icon: React.ReactNode;
    color: 'green' | 'red' | 'blue';
}

const colorClasses = {
    green: 'bg-green-100 text-green-600',
    red: 'bg-red-100 text-red-600',
    blue: 'bg-blue-100 text-blue-600',
};

const textClasses = {
    green: 'text-green-600',
    red: 'text-red-600',
    blue: 'text-blue-600',
};

export function SummaryCard({ title, value, icon, color }: SummaryCardProps) {
    const formatCurrency = (val: number) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL',
        }).format(val);
    };

    return (
        <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200 flex items-center space-x-4">
            <div className={`p-3 rounded-full ${colorClasses[color]}`}>
                <div className="text-2xl">{icon}</div>
            </div>
            <div>
                <h2 className="text-gray-500 text-sm font-medium">{title}</h2>
                <p className={`text-2xl font-semibold ${textClasses[color]}`}>{formatCurrency(value)}</p>
            </div>
        </div>
    );
}
