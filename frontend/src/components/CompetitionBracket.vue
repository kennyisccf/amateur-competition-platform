<template>
  <div class="draw-panel" @click="closeNodeMenu">
    <div class="draw-header">
      <div>
        <p class="eyebrow">抽签与淘汰树</p>
        <h3>{{ competition?.title || '赛事赛程' }}</h3>
      </div>
      <div class="draw-actions">
        <el-tag :type="competitionStatus.type" effect="light" size="large">
          {{ competitionStatus.text }}
        </el-tag>
        <el-tag effect="plain" size="large">{{ bracketMeta.playerCount }}队赛程</el-tag>
        <el-tag effect="plain" size="large">种子 {{ bracketMeta.seedCount }} 位</el-tag>
        <el-button v-if="!readonly" size="small" type="primary" @click="shuffleDraw">
          重新抽签
        </el-button>
        <el-button v-if="!readonly" size="small" @click="resetBracketWinners">
          重置晋级
        </el-button>
      </div>
    </div>

    <div class="draw-note">
      {{ readonly ? '参赛者可在这里查看当前淘汰树；晋级结果由赛事创建者或管理员维护。' : '只使用已通过报名的选手生成赛程。右键选手可设置晋级、退赛、轮空晋级或封禁。' }}
    </div>

    <el-empty v-if="bracketMeta.playerCount === 0" description="暂无已通过报名选手" />
    <div v-else class="tree-scroll">
      <svg
        class="tree-svg"
        :viewBox="`0 0 ${bracketTree.width} ${bracketTree.height}`"
        role="img"
        aria-label="赛事淘汰树"
      >
        <g class="tree-lines">
          <path
            v-for="line in bracketTree.lines"
            :key="line.key"
            class="tree-line"
            :d="line.d"
          />
        </g>

        <g v-for="title in bracketTree.roundTitles" :key="title.key">
          <text class="round-title-text" :x="title.x" :y="title.y">
            {{ title.title }}
          </text>
          <text class="round-subtitle-text" :x="title.x" :y="title.y + 18">
            {{ title.subtitle }}
          </text>
        </g>

        <g
          v-for="node in bracketTree.playerNodes"
          :key="node.key"
          class="player-node"
          :class="{
            empty: node.player.empty,
            bye: node.player.bye,
            winner: node.winner,
            seed: node.player.seedRank,
            readonly
          }"
          role="button"
          tabindex="0"
          @contextmenu.prevent.stop="openNodeMenu($event, node)"
        >
          <rect :x="node.x" :y="node.y" :width="node.width" :height="node.height" rx="8" />
          <text v-if="node.player.seedRank" class="seed-text" :x="node.x + 18" :y="node.y + 23">
            S{{ node.player.seedRank }}
          </text>
          <text class="player-name" :x="node.player.seedRank ? node.x + 42 : node.x + 14" :y="node.y + 23">
            {{ truncateName(node.player.name) }}
          </text>
          <text
            v-if="!node.player.empty && !node.player.bye"
            class="player-points"
            :x="node.x + node.width - 12"
            :y="node.y + 23"
            text-anchor="end"
          >
            {{ node.player.points }}分
          </text>
        </g>

        <g class="champion-node" :class="{ decided: Boolean(bracketChampion) }">
          <rect
            :x="bracketTree.champion.x"
            :y="bracketTree.champion.y"
            :width="bracketTree.champion.width"
            :height="bracketTree.champion.height"
            rx="10"
          />
          <text
            class="champion-label"
            :x="bracketTree.champion.x + 14"
            :y="bracketTree.champion.y + 22"
          >
            冠军
          </text>
          <text
            class="champion-name"
            :x="bracketTree.champion.x + 14"
            :y="bracketTree.champion.y + 46"
          >
            {{ truncateName(bracketChampion?.name || '待决出', 10) }}
          </text>
        </g>

        <g v-if="bracketTree.bronze" class="bronze-node" :class="{ decided: Boolean(bronzeWinner) }">
          <rect
            :x="bracketTree.bronze.x"
            :y="bracketTree.bronze.y"
            :width="bracketTree.bronze.width"
            :height="bracketTree.bronze.height"
            rx="10"
          />
          <text
            class="bronze-label"
            :x="bracketTree.bronze.x + 14"
            :y="bracketTree.bronze.y + 22"
          >
            季军
          </text>
          <text
            class="bronze-name"
            :x="bracketTree.bronze.x + 14"
            :y="bracketTree.bronze.y + 46"
          >
            {{ truncateName(bronzeWinner?.name || '待决出', 10) }}
          </text>
        </g>
      </svg>
    </div>

    <div
      v-if="nodeMenu.visible"
      class="tree-context-menu"
      :style="{ left: `${nodeMenu.x}px`, top: `${nodeMenu.y}px` }"
      @click.stop
    >
      <button type="button" @click="handleNodeMenuAction('advance')">设为晋级</button>
      <button type="button" @click="handleNodeMenuAction('walkover')">对手轮空晋级</button>
      <button type="button" @click="handleNodeMenuAction('reset')">取消本场结果</button>
      <button type="button" @click="handleNodeMenuAction('drop')">标记退赛</button>
      <button v-if="props.allowBan" type="button" class="danger" @click="handleNodeMenuAction('ban')">封禁账号</button>
    </div>

    <div class="bracket-summary">
      <div>
        <span>赛制</span>
        <strong>{{ formatCompetitionRule(competition) }}</strong>
      </div>
      <div>
        <span>已通过报名</span>
        <strong>{{ bracketMeta.playerCount }}</strong>
      </div>
      <div>
        <span>轮空名额</span>
        <strong>{{ bracketMeta.byeCount }}</strong>
      </div>
      <div>
        <span>冠军</span>
        <strong>{{ bracketChampion?.name || '待决出' }}</strong>
      </div>
      <div>
        <span>季军</span>
        <strong>{{ bronzeWinner?.name || '待决出' }}</strong>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  competition: { type: Object, default: () => ({}) },
  registrations: { type: Array, default: () => [] },
  bracketState: { type: Object, default: () => ({}) },
  readonly: { type: Boolean, default: true },
  allowBan: { type: Boolean, default: false }
})

const emit = defineEmits(['state-change', 'registration-action'])

const drawSeed = ref(Date.now())
const bracketWinners = ref({})
const nodeMenu = ref({ visible: false, x: 0, y: 0, node: null })
const byePlayer = { id: 'BYE', name: '轮空', points: 0, bye: true }
const emptyPlayer = { id: 'EMPTY', name: '待定', points: 0, empty: true }

const competitionStatusMap = {
  0: { text: '平台审核中', type: 'warning' },
  1: { text: '报名中', type: 'success' },
  2: { text: '进行中', type: 'primary' },
  3: { text: '已结束', type: 'info' },
  4: { text: '审核驳回', type: 'danger' }
}
const competitionStatus = computed(() =>
  competitionStatusMap[props.competition?.status] || { text: '未知状态', type: 'info' }
)

watch(
  () => props.bracketState,
  (state) => {
    drawSeed.value = state?.drawSeed || (props.competition?.id || 1) * 100003
    bracketWinners.value = state?.winners || {}
  },
  { immediate: true, deep: true }
)

const getRegistrationName = (item) => item?.team_name || item?.nickname || item?.username || '未命名选手'
const truncateName = (text, max = 8) => {
  const value = String(text || '')
  return value.length > max ? `${value.slice(0, max)}...` : value
}
const hashString = (value) => {
  let hash = 2166136261
  for (let i = 0; i < value.length; i += 1) {
    hash ^= value.charCodeAt(i)
    hash += (hash << 1) + (hash << 4) + (hash << 7) + (hash << 8) + (hash << 24)
  }
  return hash >>> 0
}
const seededRandom = (seed) => {
  let value = seed >>> 0
  return () => {
    value += 0x6D2B79F5
    let next = value
    next = Math.imul(next ^ (next >>> 15), next | 1)
    next ^= next + Math.imul(next ^ (next >>> 7), next | 61)
    return ((next ^ (next >>> 14)) >>> 0) / 4294967296
  }
}
const shuffleWithSeed = (items, seed) => {
  const result = items.slice()
  const random = seededRandom(seed)
  for (let i = result.length - 1; i > 0; i -= 1) {
    const j = Math.floor(random() * (i + 1))
    ;[result[i], result[j]] = [result[j], result[i]]
  }
  return result
}
const nextPowerOfTwo = (value) => {
  let size = 2
  while (size < value) size *= 2
  return size
}
const getSeedMatchOrder = (matchCount) => {
  const order = []
  const add = (index) => {
    if (index >= 0 && index < matchCount && !order.includes(index)) order.push(index)
  }
  add(0)
  add(matchCount - 1)
  add(Math.floor(matchCount / 2))
  add(Math.max(0, Math.floor(matchCount / 2) - 1))
  for (let i = 0; i < matchCount; i += 1) add(i)
  return order
}

const eligiblePlayers = computed(() =>
  props.registrations
    .filter(item => item.review_status === 1)
    .map(item => ({
      id: String(item.registration_id),
      registrationId: item.registration_id,
      userId: item.player_id,
      name: getRegistrationName(item),
      username: item.username,
      points: Number(item.player_points || 0),
      seedRank: 0
    }))
)
const bracketMeta = computed(() => {
  const playerCount = eligiblePlayers.value.length
  const slotCount = nextPowerOfTwo(Math.max(2, playerCount))
  const byeCount = Math.max(0, slotCount - playerCount)
  const seedCount = playerCount ? Math.min(playerCount, Math.max(byeCount, Math.min(4, Math.floor(playerCount / 4)))) : 0
  return { playerCount, slotCount, byeCount, seedCount }
})
const arrangedFirstRound = computed(() => {
  const { slotCount, seedCount } = bracketMeta.value
  const matchCount = slotCount / 2
  const matches = Array.from({ length: matchCount }, () => [null, null])
  const ranked = eligiblePlayers.value.slice().sort((a, b) => b.points - a.points || a.name.localeCompare(b.name))
  const seeds = ranked.slice(0, seedCount).map((item, index) => ({ ...item, seedRank: index + 1 }))
  const seedIds = new Set(seeds.map(item => item.id))
  const drawBase = hashString(`${props.competition?.id || 'event'}-${drawSeed.value}`)
  const others = shuffleWithSeed(
    eligiblePlayers.value.filter(item => !seedIds.has(item.id)),
    drawBase
  )
  const seedOrder = getSeedMatchOrder(matchCount)

  seeds.forEach((seed, index) => {
    const matchIndex = seedOrder[index] ?? index
    matches[matchIndex][0] = seed
    if (index < bracketMeta.value.byeCount) {
      matches[matchIndex][1] = { ...byePlayer, id: `BYE-${matchIndex}` }
    }
  })

  matches.forEach((match, matchIndex) => {
    for (let slotIndex = 0; slotIndex < 2; slotIndex += 1) {
      if (!match[slotIndex]) {
        match[slotIndex] = others.shift() || { ...byePlayer, id: `BYE-${matchIndex}-${slotIndex}` }
      }
    }
  })
  return matches
})
const getRoundTitle = (roundIndex, totalRounds) => {
  if (roundIndex === totalRounds - 1) return '决赛'
  if (roundIndex === totalRounds - 2) return '半决赛'
  if (roundIndex === 0) return '首轮抽签'
  return `第 ${roundIndex + 1} 轮`
}
const resolveWinner = (match) => {
  const winnerId = bracketWinners.value[match.key]
  const selected = match.players.find(player => player.id === winnerId)
  if (selected && !selected.empty && !selected.bye) return selected
  const realPlayers = match.players.filter(player => !player.empty && !player.bye)
  const hasBye = match.players.some(player => player.bye)
  if (hasBye && realPlayers.length === 1) return realPlayers[0]
  return null
}
const isRealPlayer = (player) => player && !player.empty && !player.bye
const getMatchLoser = (match) => {
  if (!match?.winner) return null
  return match.players.find(player => isRealPlayer(player) && player.id !== match.winner.id) || null
}
const bracketRounds = computed(() => {
  const rounds = []
  const totalRounds = Math.log2(bracketMeta.value.slotCount)
  let sourceMatches = arrangedFirstRound.value

  for (let roundIndex = 0; roundIndex < totalRounds; roundIndex += 1) {
    const matches = sourceMatches.map((players, matchIndex) => {
      const safePlayers = players.map((player, slotIndex) => ({
        ...player,
        slotKey: `r${roundIndex}-m${matchIndex}-s${slotIndex}`
      }))
      const match = {
        key: `r${roundIndex}-m${matchIndex}`,
        roundIndex,
        matchIndex,
        code: `M${roundIndex + 1}-${matchIndex + 1}`,
        players: safePlayers,
        winner: null,
        autoAdvance: safePlayers.some(player => player.bye),
        locked: roundIndex > 0 && safePlayers.every(player => player.empty)
      }
      match.winner = resolveWinner(match)
      return match
    })
    const remaining = bracketMeta.value.slotCount / (2 ** (roundIndex + 1))
    rounds.push({
      key: `round-${roundIndex}`,
      title: getRoundTitle(roundIndex, totalRounds),
      subtitle: roundIndex === 0 ? `${bracketMeta.value.playerCount}队参赛，${bracketMeta.value.byeCount}个轮空` : `剩余 ${remaining} 强`,
      matches
    })
    sourceMatches = []
    for (let i = 0; i < matches.length; i += 2) {
      sourceMatches.push([
        matches[i]?.winner || { ...emptyPlayer, id: `EMPTY-${roundIndex}-${i}` },
        matches[i + 1]?.winner || { ...emptyPlayer, id: `EMPTY-${roundIndex}-${i + 1}` }
      ])
    }
  }
  return rounds
})
const bracketChampion = computed(() => {
  const finalRound = bracketRounds.value[bracketRounds.value.length - 1]
  return finalRound?.matches?.[0]?.winner || null
})
const finalLoser = computed(() => {
  const finalRound = bracketRounds.value[bracketRounds.value.length - 1]
  return getMatchLoser(finalRound?.matches?.[0])
})
const bronzeMatch = computed(() => {
  if (bracketRounds.value.length < 2) return null
  const semiRound = bracketRounds.value[bracketRounds.value.length - 2]
  if (!semiRound?.matches || semiRound.matches.length < 2) return null
  const players = semiRound.matches.map(match => getMatchLoser(match)).filter(Boolean)
  if (players.length < 2) return null
  const match = {
    key: 'bronze',
    roundIndex: bracketRounds.value.length,
    matchIndex: 0,
    players: players.map((player, index) => ({
      ...player,
      slotKey: `bronze-${index}`
    })),
    winner: null
  }
  const winnerId = bracketWinners.value[match.key]
  match.winner = match.players.find(player => player.id === winnerId) || null
  return match
})
const bronzeWinner = computed(() => bronzeMatch.value?.winner || null)
const bronzeLoser = computed(() => getMatchLoser(bronzeMatch.value))
const stageLabelForRound = (roundIndex) => {
  const size = bracketMeta.value.slotCount / (2 ** roundIndex)
  return `${size}强`
}
const rankStartForRound = (roundIndex) => {
  return bracketMeta.value.slotCount / (2 ** (roundIndex + 1)) + 1
}
const addRanking = (rankings, seen, player, finalRank, finalScore) => {
  if (!isRealPlayer(player) || seen.has(player.registrationId)) return
  seen.add(player.registrationId)
  rankings.push({
    registration_id: Number(player.registrationId),
    final_rank: Number(finalRank),
    final_score: finalScore
  })
}
const bracketRankings = computed(() => {
  const rankings = []
  const seen = new Set()
  const rounds = bracketRounds.value
  rounds.forEach((round, roundIndex) => {
    round.matches.forEach((match) => {
      const loser = getMatchLoser(match)
      if (!loser) return
      const isFinal = roundIndex === rounds.length - 1
      const isSemiFinal = roundIndex === rounds.length - 2
      if (isFinal) {
        addRanking(rankings, seen, match.winner, 1, '冠军')
        addRanking(rankings, seen, loser, 2, '亚军')
      } else if (isSemiFinal) {
        if (bronzeWinner.value && bronzeLoser.value) {
          addRanking(rankings, seen, bronzeWinner.value, 3, '季军')
          addRanking(rankings, seen, bronzeLoser.value, 4, '第四名')
        } else {
          addRanking(rankings, seen, loser, 3, '四强')
        }
      } else {
        addRanking(rankings, seen, loser, rankStartForRound(roundIndex), stageLabelForRound(roundIndex))
      }
    })
  })
  return rankings
})

const bracketTree = computed(() => {
  const boxW = 178
  const boxH = 36
  const slotGap = 8
  const xStep = 250
  const top = 74
  const left = 22
  const rowGap = 94
  const connectorOffset = 26
  const rounds = bracketRounds.value
  const roundPositions = []
  const playerNodes = []
  const lines = []
  const roundTitles = []
  let lineIndex = 0

  if (!rounds.length) {
    return {
      width: 760,
      height: 220,
      lines: [],
      playerNodes: [],
      roundTitles: [],
      champion: { x: 600, y: 90, width: 138, height: 62 }
    }
  }

  rounds.forEach((round, roundIndex) => {
    const x = left + roundIndex * xStep
    roundTitles.push({
      key: `title-${roundIndex}`,
      x,
      y: 26,
      title: round.title,
      subtitle: round.subtitle
    })

    roundPositions[roundIndex] = []
    round.matches.forEach((match, matchIndex) => {
      const yCenter = roundIndex === 0
        ? top + matchIndex * rowGap
        : (roundPositions[roundIndex - 1][matchIndex * 2].yCenter + roundPositions[roundIndex - 1][matchIndex * 2 + 1].yCenter) / 2
      const firstY = yCenter - boxH - slotGap / 2
      const secondY = yCenter + slotGap / 2
      const position = {
        x,
        yCenter,
        outX: x + boxW + connectorOffset,
        slots: [
          { y: firstY, yCenter: firstY + boxH / 2 },
          { y: secondY, yCenter: secondY + boxH / 2 }
        ]
      }
      roundPositions[roundIndex][matchIndex] = position

      match.players.forEach((player, slotIndex) => {
        const slot = position.slots[slotIndex]
        playerNodes.push({
          key: `${match.key}-${slotIndex}`,
          matchKey: match.key,
          roundIndex,
          x,
          y: slot.y,
          width: boxW,
          height: boxH,
          player,
          winner: match.winner?.id === player.id
        })
      })

      const mergeX = x + boxW + 12
      const y1 = position.slots[0].yCenter
      const y2 = position.slots[1].yCenter
      lines.push({
        key: `match-${lineIndex++}`,
        d: `M ${x + boxW} ${y1} H ${mergeX} V ${y2} H ${x + boxW} M ${mergeX} ${yCenter} H ${position.outX}`
      })
    })
  })

  for (let roundIndex = 0; roundIndex < roundPositions.length - 1; roundIndex += 1) {
    roundPositions[roundIndex].forEach((position, matchIndex) => {
      const next = roundPositions[roundIndex + 1][Math.floor(matchIndex / 2)]
      const nextSlot = next.slots[matchIndex % 2]
      const targetX = next.x
      const midX = (position.outX + targetX) / 2
      lines.push({
        key: `advance-${lineIndex++}`,
        d: `M ${position.outX} ${position.yCenter} H ${midX} V ${nextSlot.yCenter} H ${targetX}`
      })
    })
  }

  const finalPosition = roundPositions[roundPositions.length - 1][0]
  const champion = {
    x: finalPosition.outX + 42,
    y: finalPosition.yCenter - 31,
    width: 150,
    height: 62
  }
  lines.push({
    key: `champion-${lineIndex++}`,
    d: `M ${finalPosition.outX} ${finalPosition.yCenter} H ${champion.x}`
  })
  let bronze = null
  if (bronzeMatch.value) {
    const baseTreeHeight = top + bracketMeta.value.slotCount / 2 * rowGap
    const bronzeX = left
    const bronzeBoxW = boxW
    const bronzeFirstY = baseTreeHeight + 34
    const bronzeSecondY = bronzeFirstY + boxH + 12
    const bronzeY1 = bronzeFirstY + boxH / 2
    const bronzeY2 = bronzeSecondY + boxH / 2
    const bronzeCenterY = (bronzeY1 + bronzeY2) / 2
    bronze = {
      x: bronzeX + bronzeBoxW + 70,
      y: bronzeCenterY - 31,
      width: 150,
      height: 62
    }
    roundTitles.push({
      key: 'title-bronze',
      x: bronzeX,
      y: bronzeFirstY - 18,
      title: '季军战',
      subtitle: '半决赛败者补赛'
    })
    bronzeMatch.value.players.forEach((player, slotIndex) => {
      const y = slotIndex === 0 ? bronzeFirstY : bronzeSecondY
      playerNodes.push({
        key: `bronze-${slotIndex}`,
        matchKey: 'bronze',
        roundIndex: rounds.length,
        x: bronzeX,
        y,
        width: bronzeBoxW,
        height: boxH,
        player,
        winner: bronzeWinner.value?.id === player.id
      })
    })
    const mergeX = bronzeX + bronzeBoxW + 12
    lines.push({
      key: `bronze-${lineIndex++}`,
      d: `M ${bronzeX + bronzeBoxW} ${bronzeY1} H ${mergeX} V ${bronzeY2} H ${bronzeX + bronzeBoxW} M ${mergeX} ${bronzeCenterY} H ${bronze.x}`
    })
  }

  return {
    width: champion.x + champion.width + 24,
    height: Math.max(
      top + bracketMeta.value.slotCount / 2 * rowGap,
      champion.y + champion.height + 56,
      bronze ? bronze.y + bronze.height + 56 : 0
    ),
    lines,
    playerNodes,
    roundTitles,
    champion,
    bronze
  }
})

const formatCompetitionRule = (item) => {
  if (!item) return '单淘汰'
  return '单淘汰'
}
const emitState = () => {
  emit('state-change', {
    drawSeed: drawSeed.value,
    winners: bracketWinners.value,
    rankings: bracketRankings.value
  })
}
const shuffleDraw = () => {
  drawSeed.value = Date.now()
  bracketWinners.value = {}
  emitState()
  ElMessage.success('已重新随机抽签')
}
const resetBracketWinners = () => {
  bracketWinners.value = {}
  emitState()
  ElMessage.success('已重置晋级结果')
}
const clearAffectedWinners = (winnerState, roundIndex) => {
  Object.keys(winnerState).forEach((key) => {
    const round = Number(key.match(/^r(\d+)-/)?.[1] || -1)
    if (round > roundIndex || (key === 'bronze' && roundIndex < bracketRounds.value.length)) {
      delete winnerState[key]
    }
  })
}
const selectTreePlayer = (node) => {
  if (props.readonly || node.player.empty || node.player.bye) return
  const next = { ...bracketWinners.value, [node.matchKey]: node.player.id }
  clearAffectedWinners(next, node.roundIndex)
  bracketWinners.value = next
  emitState()
}
const findMatchByKey = (matchKey) => {
  if (matchKey === 'bronze') return bronzeMatch.value
  return bracketRounds.value.flatMap(round => round.matches).find(match => match.key === matchKey)
}
const selectOpponentPlayer = (node) => {
  const match = findMatchByKey(node.matchKey)
  const opponent = match?.players?.find(player => isRealPlayer(player) && player.id !== node.player.id)
  if (!opponent) {
    ElMessage.warning('当前没有可自动晋级的对手')
    return
  }
  const next = { ...bracketWinners.value, [node.matchKey]: opponent.id }
  clearAffectedWinners(next, node.roundIndex)
  bracketWinners.value = next
  emitState()
  ElMessage.success(`已让“${opponent.name}”轮空晋级`)
}
const resetTreeMatch = (node) => {
  const next = { ...bracketWinners.value }
  delete next[node.matchKey]
  clearAffectedWinners(next, node.roundIndex)
  bracketWinners.value = next
  emitState()
}
const closeNodeMenu = () => {
  nodeMenu.value.visible = false
}
const openNodeMenu = (event, node) => {
  if (props.readonly || node.player.empty || node.player.bye) return
  const panel = event.currentTarget.closest('.draw-panel')
  const rect = panel.getBoundingClientRect()
  nodeMenu.value = {
    visible: true,
    x: event.clientX - rect.left,
    y: event.clientY - rect.top,
    node
  }
}
const handleNodeMenuAction = (action) => {
  const node = nodeMenu.value.node
  closeNodeMenu()
  if (!node) return
  if (action === 'advance') {
    selectTreePlayer(node)
    return
  }
  if (action === 'walkover') {
    selectOpponentPlayer(node)
    return
  }
  if (action === 'reset') {
    resetTreeMatch(node)
    return
  }
  if (action === 'drop' || action === 'ban') {
    selectOpponentPlayer(node)
  }
  emit('registration-action', {
    action,
    registrationId: node.player.registrationId,
    playerId: node.player.userId,
    username: node.player.username,
    name: node.player.name
  })
}
</script>

<style scoped>
.draw-panel {
  position: relative;
  width: 100%;
  max-width: 100%;
  margin-top: 24px;
  padding: 20px;
  background: #fff;
  border: 1px solid #e5eef9;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(46, 91, 145, 0.08);
  overflow: hidden;
  box-sizing: border-box;
}
.draw-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 12px;
}
.eyebrow {
  margin: 0 0 6px;
  color: #5d7da3;
  font-size: 13px;
}
.draw-header h3 {
  margin: 0;
  color: #15253f;
  font-size: 20px;
  font-weight: 600;
}
.draw-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.draw-note {
  margin-bottom: 12px;
  padding: 10px 12px;
  color: #5d6f86;
  background: #f6f9fd;
  border: 1px solid #e8eff8;
  border-radius: 8px;
  font-size: 13px;
}
.tree-scroll {
  width: 100%;
  max-width: 100%;
  overflow: hidden;
  padding: 12px;
  background: #f7faff;
  border: 1px solid #edf2f8;
  border-radius: 8px;
  box-sizing: border-box;
  scrollbar-width: none;
}
.tree-scroll::-webkit-scrollbar {
  width: 0;
  height: 0;
}
.tree-svg {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  height: auto;
  display: block;
}
.tree-line {
  fill: none;
  stroke: #4d7fbd;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  vector-effect: non-scaling-stroke;
}
.round-title-text {
  fill: #1f4f89;
  font-size: 15px;
  font-weight: 700;
}
.round-subtitle-text {
  fill: #738196;
  font-size: 12px;
}
.player-node {
  cursor: context-menu;
}
.player-node rect {
  fill: #ffffff;
  stroke: #dfe8f5;
  stroke-width: 1.4;
}
.player-node:hover:not(.empty):not(.bye):not(.readonly) rect {
  fill: #eef6ff;
  stroke: #409eff;
}
.player-node.winner rect {
  fill: #edf8f2;
  stroke: #67c23a;
  stroke-width: 2;
}
.player-node.seed rect {
  fill: #fff8ec;
  stroke: #e6a23c;
}
.player-node.empty,
.player-node.bye,
.player-node.readonly {
  cursor: default;
}
.tree-context-menu {
  position: absolute;
  z-index: 20;
  width: 150px;
  padding: 6px;
  background: #fff;
  border: 1px solid #dce6f4;
  border-radius: 8px;
  box-shadow: 0 12px 30px rgba(39, 68, 105, 0.18);
}
.tree-context-menu button {
  width: 100%;
  padding: 8px 10px;
  color: #26364d;
  background: transparent;
  border: 0;
  border-radius: 6px;
  text-align: left;
  cursor: pointer;
}
.tree-context-menu button:hover {
  background: #eef5ff;
}
.tree-context-menu button.danger {
  color: #c45656;
}
.tree-context-menu button.danger:hover {
  background: #fff2f0;
}
.player-node.empty rect,
.player-node.bye rect {
  fill: #f2f5fa;
  stroke: #dbe3ef;
}
.seed-text {
  fill: #9a5b00;
  font-size: 12px;
  font-weight: 800;
}
.player-name {
  fill: #23344f;
  font-size: 13px;
  font-weight: 700;
}
.player-node.empty .player-name,
.player-node.bye .player-name {
  fill: #8c9aab;
}
.player-points {
  fill: #74849a;
  font-size: 12px;
}
.champion-node rect {
  fill: #eef3fb;
  stroke: #cfdbea;
  stroke-width: 1.4;
}
.bronze-node rect {
  fill: #fff8ec;
  stroke: #e7c48a;
  stroke-width: 1.4;
}
.champion-node.decided rect {
  fill: #285da7;
  stroke: #204d8d;
}
.bronze-node.decided rect {
  fill: #b7791f;
  stroke: #9a5f12;
}
.champion-label {
  fill: #55708e;
  font-size: 13px;
  font-weight: 700;
}
.bronze-label {
  fill: #8a5a12;
  font-size: 13px;
  font-weight: 700;
}
.champion-name {
  fill: #26364d;
  font-size: 16px;
  font-weight: 800;
}
.bronze-name {
  fill: #4a3210;
  font-size: 16px;
  font-weight: 800;
}
.champion-node.decided .champion-label,
.champion-node.decided .champion-name,
.bronze-node.decided .bronze-label,
.bronze-node.decided .bronze-name {
  fill: #fff;
}
.bracket-summary {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-top: 16px;
}
.bracket-summary div {
  padding: 12px 14px;
  background: #f9fbff;
  border: 1px solid #edf1f6;
  border-radius: 8px;
}
.bracket-summary span {
  display: block;
  margin-bottom: 4px;
  color: #7a8797;
  font-size: 12px;
}
.bracket-summary strong {
  color: #1f2d3d;
  font-size: 15px;
}
@media (max-width: 960px) {
  .draw-header {
    flex-direction: column;
  }
  .bracket-summary {
    grid-template-columns: 1fr;
  }
  .tree-svg {
    width: auto;
  }
}
</style>
