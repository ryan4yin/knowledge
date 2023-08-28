use_synth :piano

# 主旋律：八辈子
song = [[3, 1], [5, 1], [3, 1], [3, 0.5],
        [5, 0.5], [10, 1], [10, 1], [10, 0.5],
        [7, 0.5], [5, 0.5], [7, 0.5], [5, 1],
        [3, 1], [3, 1], [3, 0.5], [5, 0.5],
        [5, 1], [3, 1], [3, 1], [-2, 0.5], [-2, 0.5]]

# 伴奏：八辈子
chords = [3, -2, 3, 5, 7, 5, 10, 7,
          3, -2, 3, 5, 7, 5, 10, 7,
          -2, -2, 3, 5, 7, 5, 10, 7,
          -2, -2, 3, 5, 7, 5, 7, 10]

live_loop :song do
  idx = tick
  play 70 + song[idx][0], release: song[idx][1] * 0.5
  sleep song[idx][1] * 0.5
end

live_loop :chord do
  idx = tick
  play 70 + chords[idx], release: 0.25, amp: 0.35
  sleep 0.25
end
