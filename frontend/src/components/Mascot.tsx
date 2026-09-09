import type { CSSProperties } from 'react'
import type { MascotExpression } from '../api/types'

interface MascotProps {
  stage: number
  expression: MascotExpression
  color: string
  unlockedFeatures?: string[]
  size?: number
}

const EXPRESSION_LABEL: Record<MascotExpression, string> = {
  idle: 'tranquilo',
  happy: 'contente',
  proud: 'orgulhoso',
  celebrating: 'comemorando',
  caring: 'acolhedor',
  tired: 'cansado',
}

// Renderização pura — nenhuma regra de estado aqui (MASCOT.md: regras no
// backend, este componente só desenha). Expressão = troca instantânea de
// olhos/boca (limitação V1 registrada em DOCUMENTATION_AUDIT.md); animação
// é só CSS (bob de repouso, pulso ao comemorar), desligada por
// prefers-reduced-motion.

function Face({ expression }: { expression: MascotExpression }) {
  const eyeY = expression === 'tired' || expression === 'caring' ? 54 : 50
  return (
    <g className="mascot-face" fill="var(--text-h, #08060d)" stroke="none">
      {expression === 'celebrating' ? (
        <>
          <path d="M34 52 l6 -6 6 6" fill="none" stroke="var(--text-h, #08060d)" strokeWidth="3" strokeLinecap="round" />
          <path d="M54 52 l6 -6 6 6" fill="none" stroke="var(--text-h, #08060d)" strokeWidth="3" strokeLinecap="round" />
          <circle cx="50" cy="66" r="6" />
        </>
      ) : expression === 'tired' ? (
        <>
          <rect x="34" y={eyeY} width="12" height="3" rx="1.5" />
          <rect x="54" y={eyeY} width="12" height="3" rx="1.5" />
          <rect x="40" y="66" width="20" height="3" rx="1.5" />
        </>
      ) : (
        <>
          <circle cx="40" cy={eyeY} r="4.5" />
          <circle cx="60" cy={eyeY} r="4.5" />
          {expression === 'caring' && (
            <>
              <ellipse cx="33" cy="62" rx="5" ry="3" fill="var(--accent, #aa3bff)" opacity="0.35" />
              <ellipse cx="67" cy="62" rx="5" ry="3" fill="var(--accent, #aa3bff)" opacity="0.35" />
              <path d="M40 66 q10 6 20 0" fill="none" stroke="var(--text-h, #08060d)" strokeWidth="3" strokeLinecap="round" />
            </>
          )}
          {(expression === 'happy' || expression === 'proud') && (
            <path d="M38 64 q12 12 24 0" fill="none" stroke="var(--text-h, #08060d)" strokeWidth="3.5" strokeLinecap="round" />
          )}
          {expression === 'idle' && (
            <path d="M42 66 q8 5 16 0" fill="none" stroke="var(--text-h, #08060d)" strokeWidth="3" strokeLinecap="round" />
          )}
        </>
      )}
    </g>
  )
}

export function Mascot({
  stage,
  expression,
  color,
  unlockedFeatures = [],
  size = 96,
}: MascotProps) {
  const has = (feature: string) => unlockedFeatures.includes(feature)
  const showCrown = stage >= 5 || has('item_crown')
  const showScarf = stage >= 2 || has('item_scarf')
  const showAntenna = stage >= 3
  const glow = stage >= 4 || has('detail_aura')

  const style = { '--mascot-color': color, width: size, height: size } as CSSProperties

  return (
    <div
      className="mascot"
      data-stage={stage}
      data-expression={expression}
      role="img"
      aria-label={`Mascote TEYO — estágio ${stage}, ${EXPRESSION_LABEL[expression] ?? expression}`}
      style={style}
    >
      <svg viewBox="0 0 100 100" width="100%" height="100%" aria-hidden="true">
        {glow && (
          <rect x="14" y="18" width="72" height="74" rx="30" fill="var(--mascot-color)" opacity="0.18" />
        )}
        {showAntenna && (
          <>
            <line x1="35" y1="20" x2="30" y2="8" stroke="var(--mascot-color)" strokeWidth="4" strokeLinecap="round" />
            <line x1="65" y1="20" x2="70" y2="8" stroke="var(--mascot-color)" strokeWidth="4" strokeLinecap="round" />
            <circle cx="30" cy="7" r="3" fill="var(--mascot-color)" />
            <circle cx="70" cy="7" r="3" fill="var(--mascot-color)" />
          </>
        )}
        <rect
          className="mascot-body"
          x="18"
          y="22"
          width="64"
          height="66"
          rx="26"
          fill="var(--mascot-color)"
        />
        {showScarf && (
          <rect x="20" y="70" width="60" height="10" rx="5" fill="var(--accent, #aa3bff)" opacity="0.85" />
        )}
        {showCrown && (
          <path d="M34 20 l6 -12 10 8 10 -8 6 12 z" fill="#f5b301" stroke="#c98f00" strokeWidth="1.5" />
        )}
        <Face expression={expression} />
        {has('detail_star') && <path d="M84 30 l2 5 5 0 -4 4 1.5 5 -4.5 -3 -4.5 3 1.5 -5 -4 -4 5 0 z" fill="#f5b301" />}
      </svg>
    </div>
  )
}
