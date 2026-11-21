/**
 * hooks/useLogStream.js
 *
 * WebSocket-based real-time log streaming
 * for a specific simulation session.
 */

import { useEffect, useRef, useState } from 'react'

import { getWebSocketUrl } from '../api/client'

export function useLogStream(
  sessionId,
  logType,
  enabled = true,
) {
  const [lines, setLines] = useState([])
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState(null)

  const socketRef = useRef(null)

  useEffect(() => {

    if (
      !enabled ||
      !sessionId ||
      !logType
    ) {
      return undefined
    }

    const socket = new WebSocket(
      getWebSocketUrl(
        `/ws/logs/${sessionId}/${logType}`,
      ),
    )

    socketRef.current = socket

    socket.onopen = () => {
      setConnected(true)
      setError(null)
    }

    socket.onmessage = (event) => {

      try {

        const payload = JSON.parse(
          event.data
        )

        if (
          payload.type === 'snapshot'
        ) {

          setLines(
            payload.lines || []
          )
        }

        if (
          payload.type === 'append'
        ) {

          setLines((current) => [
            ...current,
            ...(payload.lines || []),
          ])
        }

      } catch {

        setError(
          'Failed to parse log stream message'
        )
      }
    }

    socket.onerror = () => {

      setError(
        'Log stream connection failed'
      )

      setConnected(false)
    }

    socket.onclose = () => {
      setConnected(false)
    }

    const heartbeat = setInterval(() => {

      if (
        socket.readyState ===
        WebSocket.OPEN
      ) {

        socket.send('ping')
      }

    }, 25000)

    return () => {

      clearInterval(heartbeat)

      socket.close()

      socketRef.current = null
    }

  }, [
    sessionId,
    logType,
    enabled,
  ])

  return {
    lines,
    lineCount: lines.length,
    connected,
    error,
  }
}