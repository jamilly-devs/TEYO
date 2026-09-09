import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Mascot } from './Mascot'

describe('Mascot', () => {
  it('reflects stage, expression and color', () => {
    render(<Mascot stage={3} expression="proud" color="#123abc" />)
    const el = screen.getByRole('img', { name: /mascote teyo/i })
    expect(el).toHaveAttribute('data-stage', '3')
    expect(el).toHaveAttribute('data-expression', 'proud')
    expect(el).toHaveStyle({ '--mascot-color': '#123abc' })
  })

  it('names the expression in the accessible label', () => {
    render(<Mascot stage={1} expression="caring" color="#000000" />)
    expect(
      screen.getByRole('img', { name: /acolhedor/i }),
    ).toBeInTheDocument()
  })

  it('shows a crown when an achievement unlocked it, regardless of stage', () => {
    const { container } = render(
      <Mascot stage={1} expression="idle" color="#000000" unlockedFeatures={['item_crown']} />,
    )
    // a coroa é um <path> amarelo — presente mesmo no estágio 1
    expect(container.querySelector('path[fill="#f5b301"]')).not.toBeNull()
  })
})
