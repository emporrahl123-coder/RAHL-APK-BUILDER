import { render, screen } from '@testing-library/react';
import App from './App';

test('renders Rahl AI title', () => {
  render(<App />);
  const titleElement = screen.getByText(/Rahl AI/i);
  expect(titleElement).toBeInTheDocument();
});
