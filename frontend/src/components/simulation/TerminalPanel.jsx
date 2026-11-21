/**
 * components/simulation/TerminalPanel.jsx
 *
 * Interactive xterm.js shell connected to the active simulation engine.
 */

import { useCallback, useEffect, useRef } from 'react'
import { Terminal } from 'xterm'
import 'xterm/css/xterm.css'

import { executeTerminalCommand } from '../../api/terminalApi'
import { useSimulationContext } from '../../context/SimulationContext'
import Card from '../ui/Card'

import './simulation.css'

function welcome(engine) {
  const mode = engine === 'docker' ? 'Docker Lab' : 'Simulation Mode'
  return [
  '\r\n\x1b[36m╔══════════════════════════════════════════════════╗\x1b[0m',
  `\r\n\x1b[36m║  SOC Investigation Terminal — ${mode.padEnd(18)}║\x1b[0m`,
  '\r\n\x1b[36m║  Type \x1b[33mhelp\x1b[36m for supported commands                  ║\x1b[0m',
  '\r\n\x1b[36m╚══════════════════════════════════════════════════╝\x1b[0m',
  '\r\n',
  ].join('')
}

export default function TerminalPanel({ engine }) {
  const terminalRef = useRef(null)
  const xtermRef = useRef(null)
  const inputBufferRef = useRef('')
  const historyRef = useRef([])
  const historyIndexRef = useRef(-1)
  const { session } = useSimulationContext()

  const writePrompt = useCallback((term, prompt = 'analyst@soc-workstation:~$ ') => {
    term.write(`\r\n\x1b[32m${prompt}\x1b[0m`)
  }, [])

  const executeCommand = useCallback(
    async (term, command) => {
      if (command.trim()) {
        historyRef.current.unshift(command)
        historyIndexRef.current = -1
      }

      try {
        const result = await executeTerminalCommand(command, session?.id)

        if (result.output === '__CLEAR__') {
          term.clear()
          term.write(welcome(engine))
        } else if (result.output) {
          term.write(`\r\n${result.output}`)
        }

        if (result.exit_code !== 0 && result.output !== '__CLEAR__') {
          term.write(`\r\n\x1b[31m[exit ${result.exit_code}]\x1b[0m`)
        }
      } catch (error) {
        term.write(`\r\n\x1b[31mError: ${error.message}\x1b[0m`)
      }

      writePrompt(term, 'analyst@soc-workstation:~$ ')
    },
    [engine, session, writePrompt],
  )

  useEffect(() => {
    if (!terminalRef.current || xtermRef.current) return

    const term = new Terminal({
      cursorBlink: true,
      fontFamily: 'Cascadia Code, Consolas, monospace',
      fontSize: 13,
      theme: {
        background: '#0a0f18',
        foreground: '#e2e8f0',
        cursor: '#22d3ee',
        selectionBackground: 'rgba(34, 211, 238, 0.25)',
      },
      rows: 22,
    })

    term.open(terminalRef.current)
    term.write(welcome(engine))
    writePrompt(term)

    term.onData((data) => {
      const code = data.charCodeAt(0)

      if (code === 13) {
        const command = inputBufferRef.current
        term.write('\r\n')
        executeCommand(term, command)
        inputBufferRef.current = ''
        return
      }

      if (code === 127) {
        if (inputBufferRef.current.length > 0) {
          inputBufferRef.current = inputBufferRef.current.slice(0, -1)
          term.write('\b \b')
        }
        return
      }

      if (data === '\u001b[A') {
        const nextIndex = historyIndexRef.current + 1
        if (nextIndex < historyRef.current.length) {
          historyIndexRef.current = nextIndex
          const historic = historyRef.current[nextIndex]
          term.write('\r\x1b[K')
          writePrompt(term)
          term.write(historic)
          inputBufferRef.current = historic
        }
        return
      }

      if (data === '\u001b[B') {
        if (historyIndexRef.current > 0) {
          historyIndexRef.current -= 1
          const historic = historyRef.current[historyIndexRef.current]
          term.write('\r\x1b[K')
          writePrompt(term)
          term.write(historic)
          inputBufferRef.current = historic
        } else if (historyIndexRef.current === 0) {
          historyIndexRef.current = -1
          term.write('\r\x1b[K')
          writePrompt(term)
          inputBufferRef.current = ''
        }
        return
      }

      if (code >= 32) {
        inputBufferRef.current += data
        term.write(data)
      }
    })

    xtermRef.current = term

    const resizeObserver = new ResizeObserver(() => {
      if (terminalRef.current) {
        const height = terminalRef.current.clientHeight
        const rows = Math.max(12, Math.floor(height / 18))
        term.resize(term.cols, rows)
      }
    })

    resizeObserver.observe(terminalRef.current)

    return () => {
      resizeObserver.disconnect()
      term.dispose()
      xtermRef.current = null
    }
  }, [engine, executeCommand, writePrompt])

  return (
    <Card
      className="terminal-panel"
      title="Investigation Terminal"
      subtitle={engine === 'docker' ? 'Interactive shell — session-isolated Docker lab' : 'Interactive shell — simulation environment'}
    >
      <div className="terminal-panel__container" ref={terminalRef} />
    </Card>
  )
}
