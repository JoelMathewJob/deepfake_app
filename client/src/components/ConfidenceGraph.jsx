import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const ConfidenceGraph = ({ realScores, fakeScores, frameIndices }) => {
  const data = {
    labels: frameIndices,
    datasets: [
      {
        label: 'Real Scores',
        data: realScores,
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
      },
      {
        label: 'Fake Scores',
        data: fakeScores,
        backgroundColor: 'rgba(255, 99, 132, 0.6)',
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Real vs Fake Confidence Scores',
      },
    },
  };

  return <Bar data={data} options={options} />;
};

export default ConfidenceGraph;