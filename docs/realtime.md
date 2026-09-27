# Realtime

Les mutations applicatives sont conçues pour produire des événements de domaine. Une prochaine itération diffusera ces événements via SSE/WebSocket pour notifications, présence et activité. Redis est déjà présent pour fournir le fan-out et les limites de débit.
