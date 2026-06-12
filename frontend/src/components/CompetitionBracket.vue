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
        <el-tag effect="plain" size="large">保送种子 {{ bracketMeta.seedCount }} 位</el-tag>
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
        :style="{ width: `${bracketTree.width}px`, height: `${bracketTree.height}px` }"
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
        <span>首轮保送</span>
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
const manualSeedIds = ref([])
const seedMode = ref('AUTO')
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
    manualSeedIds.value = Array.isArray(state?.seedIds) ? state.seedIds.map(String) : []
    seedMode.value = state?.seedMode === 'MANUAL' ? 'MANUAL' : 'AUTO'
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
const floorPowerOfTwo = (value) => {
  let size = 1
  while (size * 2 <= value) size *= 2
  return size
}
const getBracketCounts = (playerCount) => {
  if (playerCount <= 1) {
    return {
      mainSize: Math.max(1, playerCount),
      prelimMatchCount: 0,
      prelimPlayerCount: 0,
      directSlotCount: playerCount,
      byeCount: 0
    }
  }
  const mainSize = floorPowerOfTwo(playerCount)
  const prelimMatchCount = playerCount - mainSize
  const prelimPlayerCount = prelimMatchCount * 2
  const directSlotCount = playerCount - prelimPlayerCount
  return {
    mainSize,
    prelimMatchCount,
    prelimPlayerCount,
    directSlotCount,
    byeCount: prelimMatchCount > 0 ? directSlotCount : 0
  }
}
const getRecommendedSeedCount = (playerCount) => {
  const { byeCount, prelimMatchCount } = getBracketCounts(playerCount)
  if (playerCount < 4 || byeCount <= 0 || prelimMatchCount <= 0) return 0
  return Math.min(byeCount, prelimMatchCount, 4, Math.ceil(playerCount / 4))
}
const getPairedSlotIndex = (slotIndex) => (slotIndex % 2 === 0 ? slotIndex + 1 : slotIndex - 1)
const getSeedSlotOrder = (slotCount) => {
  const order = []
  const add = (index) => {
    if (index >= 0 && index < slotCount && !order.includes(index)) order.push(index)
  }
  add(0)
  add(slotCount - 1)
  add(Math.floor(slotCount / 2))
  add(Math.max(0, Math.floor(slotCount / 2) - 1))
  let step = Math.max(1, Math.floor(slotCount / 4))
  while (step >= 1) {
    for (let i = 0; i < slotCount; i += step) add(i)
    if (step === 1) break
    step = Math.floor(step / 2)
  }
  for (let i = 0; i < slotCount; i += 1) add(i)
  return order
}
const getProtectedSeedSlots = (slotCount, seedCount) => {
  const slots = []
  const blocked = new Set()
  getSeedSlotOrder(slotCount).forEach((slot) => {
    const paired = getPairedSlotIndex(slot)
    if (
      slots.length < seedCount
      && paired >= 0
      && paired < slotCount
      && !blocked.has(slot)
      && !blocked.has(paired)
    ) {
      slots.push(slot)
      blocked.add(slot)
      blocked.add(paired)
    }
  })
  return slots
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
const rankedPlayers = computed(() =>
  eligiblePlayers.value.slice().sort((a, b) => b.points - a.points || a.name.localeCompare(b.name))
)
const autoSeedIds = computed(() => {
  const playerCount = eligiblePlayers.value.length
  const seedCount = getRecommendedSeedCount(playerCount)
  if (!seedCount) return []
  return rankedPlayers.value.slice(0, seedCount).map(item => item.id)
})
const activeSeedIds = computed(() => {
  const valid = new Set(eligiblePlayers.value.map(item => item.id))
  const source = seedMode.value === 'MANUAL' ? manualSeedIds.value : autoSeedIds.value
  return source
    .map(String)
    .filter((id, index, arr) => valid.has(id) && arr.indexOf(id) === index)
    .slice(0, getRecommendedSeedCount(eligiblePlayers.value.length))
})
const bracketMeta = computed(() => {
  const playerCount = eligiblePlayers.value.length
  const counts = getBracketCounts(playerCount)
  if (playerCount <= 1) {
    return {
      playerCount,
      slotCount: Math.max(1, playerCount),
      ...counts,
      seedCount: 0,
      seedMode: seedMode.value
    }
  }
  return {
    playerCount,
    slotCount: counts.mainSize,
    ...counts,
    seedCount: activeSeedIds.value.length,
    seedMode: seedMode.value
  }
})

const arrangedDraw = computed(() => {
  const players = eligiblePlayers.value
  const playerCount = players.length
  if (playerCount === 0) {
    return { directPlayers: [], prelimMatches: [], mainSlots: [], mainSize: 0 }
  }
  if (playerCount === 1) {
    return { directPlayers: [players[0]], prelimMatches: [], mainSlots: [players[0]], mainSize: 1 }
  }

  const { mainSize, prelimMatchCount, directSlotCount } = bracketMeta.value
  const drawBase = hashString(`${props.competition?.id || 'event'}-${drawSeed.value}`)
  if (prelimMatchCount === 0) {
    return {
      directPlayers: [],
      prelimMatches: [],
      mainSlots: shuffleWithSeed(players, drawBase),
      mainSize
    }
  }
  const activeSeeds = activeSeedIds.value
    .map(id => players.find(item => item.id === id))
    .filter(Boolean)
    .map((item, index) => ({ ...item, seedRank: index + 1 }))
  const seedIdSet = new Set(activeSeeds.map(item => item.id))
  const shuffledRemaining = shuffleWithSeed(players.filter(item => !seedIdSet.has(item.id)), drawBase + 17)
  const directNonSeeds = shuffledRemaining.slice(0, Math.max(0, directSlotCount - activeSeeds.length))
  const directPlayers = [...activeSeeds, ...directNonSeeds]
  const directIdSet = new Set(directPlayers.map(item => item.id))
  const prelimPlayers = shuffleWithSeed(players.filter(item => !directIdSet.has(item.id)), drawBase)
  const mainSlots = Array.from({ length: mainSize }, () => null)
  const slotOrder = getSeedSlotOrder(mainSize)
  const occupiedSlots = new Set()
  const seedSlots = getProtectedSeedSlots(mainSize, activeSeeds.length)

  activeSeeds.forEach((player, index) => {
    const slot = seedSlots[index] ?? slotOrder.find(item => !occupiedSlots.has(item))
    if (slot === undefined) return
    mainSlots[slot] = player
    occupiedSlots.add(slot)
  })

  const protectedPrelimSlots = seedSlots
    .map(getPairedSlotIndex)
    .filter(slot => slot >= 0 && slot < mainSize && !occupiedSlots.has(slot))
  const targetSlotIndices = []
  protectedPrelimSlots.forEach((slot) => {
    targetSlotIndices.push(slot)
    occupiedSlots.add(slot)
  })
  slotOrder.forEach((slot) => {
    if (targetSlotIndices.length >= prelimMatchCount) return
    if (!occupiedSlots.has(slot)) {
      targetSlotIndices.push(slot)
      occupiedSlots.add(slot)
    }
  })

  directNonSeeds.forEach((player) => {
    const slot = slotOrder.find(item => !occupiedSlots.has(item)) ?? mainSlots.findIndex(item => !item)
    if (slot === undefined || slot < 0) return
    mainSlots[slot] = player
    occupiedSlots.add(slot)
  })

  const prelimMatches = []
  for (let index = 0; index < prelimMatchCount; index += 1) {
    const targetSlotIndex = targetSlotIndices[index] ?? mainSlots.findIndex(item => !item)
    const matchKey = `p0-m${index}`
    const placeholder = {
      id: `PRELIM-WINNER-${index}`,
      name: `预赛胜者${index + 1}`,
      points: 0,
      empty: true,
      pending: true,
      sourceMatchKey: matchKey
    }
    mainSlots[targetSlotIndex] = placeholder
    prelimMatches.push({
      key: matchKey,
      roundIndex: 0,
      matchIndex: index,
      targetSlotIndex,
      players: [
        prelimPlayers[index * 2] || { ...emptyPlayer, id: `EMPTY-P-${index}-0` },
        prelimPlayers[index * 2 + 1] || { ...emptyPlayer, id: `EMPTY-P-${index}-1` }
      ],
      loserRank: mainSize + 1,
      loserScore: '预赛'
    })
  }

  return { directPlayers, prelimMatches, mainSlots, mainSize }
})

const resolveWinner = (match) => {
  const winnerId = bracketWinners.value[match.key]
  const selected = match.players.find(player => player.id === winnerId)
  if (selected && !selected.empty && !selected.bye && !selected.pending) return selected
  const realPlayers = match.players.filter(player => !player.empty && !player.bye && !player.pending)
  const hasBye = match.players.some(player => player.bye)
  if (hasBye && realPlayers.length === 1) return realPlayers[0]
  return null
}
const isRealPlayer = (player) => player && !player.empty && !player.bye && !player.pending
const getMatchLoser = (match) => {
  if (!match?.winner) return null
  return match.players.find(player => isRealPlayer(player) && player.id !== match.winner.id) || null
}
const getRoundTitle = (mainRoundIndex, totalMainRounds) => {
  if (mainRoundIndex === totalMainRounds - 1) return '决赛'
  if (mainRoundIndex === totalMainRounds - 2) return '半决赛'
  if (mainRoundIndex === 0) return '正赛首轮'
  return `正赛第 ${mainRoundIndex + 1} 轮`
}

const bracketRounds = computed(() => {
  const rounds = []
  const draw = arrangedDraw.value
  if (!draw.mainSize) return rounds

  const prelimMatches = draw.prelimMatches.map((match) => {
    const safePlayers = match.players.map((player, slotIndex) => ({
      ...player,
      slotKey: `${match.key}-s${slotIndex}`
    }))
    const next = {
      ...match,
      type: 'preliminary',
      title: '预赛',
      players: safePlayers,
      winner: null,
      autoAdvance: false,
      locked: false
    }
    next.winner = resolveWinner(next)
    return next
  })
  if (prelimMatches.length) {
    rounds.push({
      key: 'round-preliminary',
      type: 'preliminary',
      title: '预赛',
      subtitle: `${prelimMatches.length} 场，胜者进入 ${draw.mainSize} 强正赛`,
      matches: prelimMatches
    })
  }

  if (draw.mainSize === 1) return rounds

  const prelimWinnerMap = Object.fromEntries(prelimMatches.map(match => [match.key, match.winner]))
  const resolvedMainSlots = draw.mainSlots.map((slot, index) => {
    if (slot?.pending) return prelimWinnerMap[slot.sourceMatchKey] || slot
    return slot || { ...byePlayer, id: `BYE-MAIN-${index}` }
  })

  let sourceMatches = []
  for (let i = 0; i < resolvedMainSlots.length; i += 2) {
    sourceMatches.push([
      resolvedMainSlots[i] || { ...emptyPlayer, id: `EMPTY-M-${i}` },
      resolvedMainSlots[i + 1] || { ...emptyPlayer, id: `EMPTY-M-${i + 1}` }
    ])
  }

  const totalMainRounds = Math.log2(draw.mainSize)
  const offset = prelimMatches.length ? 1 : 0
  for (let mainRoundIndex = 0; mainRoundIndex < totalMainRounds; mainRoundIndex += 1) {
    const roundIndex = mainRoundIndex + offset
    const matches = sourceMatches.map((players, matchIndex) => {
      const safePlayers = players.map((player, slotIndex) => ({
        ...player,
        slotKey: `r${mainRoundIndex}-m${matchIndex}-s${slotIndex}`
      }))
      const remainingAfterRound = draw.mainSize / (2 ** (mainRoundIndex + 1))
      const match = {
        key: `r${mainRoundIndex}-m${matchIndex}`,
        type: 'main',
        roundIndex,
        mainRoundIndex,
        matchIndex,
        code: `M${mainRoundIndex + 1}-${matchIndex + 1}`,
        players: safePlayers,
        winner: null,
        autoAdvance: safePlayers.some(player => player.bye),
        locked: mainRoundIndex > 0 && safePlayers.every(player => player.empty || player.pending),
        loserRank: remainingAfterRound + 1,
        loserScore: remainingAfterRound <= 1 ? '亚军' : `止步${remainingAfterRound * 2}强`
      }
      match.winner = resolveWinner(match)
      return match
    })
    rounds.push({
      key: `round-main-${mainRoundIndex}`,
      type: 'main',
      title: getRoundTitle(mainRoundIndex, totalMainRounds),
      subtitle: mainRoundIndex === 0
        ? `${draw.mainSize} 强正赛，${bracketMeta.value.byeCount} 人直接入围`
        : `剩余 ${draw.mainSize / (2 ** mainRoundIndex)} 强`,
      matches
    })
    sourceMatches = []
    for (let i = 0; i < matches.length; i += 2) {
      sourceMatches.push([
        matches[i]?.winner || { ...emptyPlayer, id: `EMPTY-${mainRoundIndex}-${i}` },
        matches[i + 1]?.winner || { ...emptyPlayer, id: `EMPTY-${mainRoundIndex}-${i + 1}` }
      ])
    }
  }
  return rounds
})

const mainRounds = computed(() => bracketRounds.value.filter(round => round.type === 'main'))
const bracketChampion = computed(() => {
  if (arrangedDraw.value.mainSize === 1) return arrangedDraw.value.directPlayers[0] || null
  const finalRound = mainRounds.value[mainRounds.value.length - 1]
  return finalRound?.matches?.[0]?.winner || null
})
const bronzeMatch = computed(() => {
  if (mainRounds.value.length < 2) return null
  const semiRound = mainRounds.value[mainRounds.value.length - 2]
  if (!semiRound?.matches || semiRound.matches.length < 2) return null
  const players = semiRound.matches.map(match => getMatchLoser(match)).filter(Boolean)
  if (players.length < 2) return null
  const match = {
    key: 'bronze',
    type: 'bronze',
    roundIndex: bracketRounds.value.length,
    matchIndex: 0,
    players: players.map((player, index) => ({
      ...player,
      slotKey: `bronze-${index}`
    })),
    winner: null,
    loserRank: 4,
    loserScore: '第四名'
  }
  const winnerId = bracketWinners.value[match.key]
  match.winner = match.players.find(player => player.id === winnerId) || null
  return match
})
const bronzeWinner = computed(() => bronzeMatch.value?.winner || null)
const bronzeLoser = computed(() => getMatchLoser(bronzeMatch.value))
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
  mainRounds.value.forEach((round, roundIndex) => {
    round.matches.forEach((match) => {
      const loser = getMatchLoser(match)
      if (!loser) return
      const isFinal = roundIndex === mainRounds.value.length - 1
      const isSemiFinal = roundIndex === mainRounds.value.length - 2
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
        addRanking(rankings, seen, loser, match.loserRank, match.loserScore)
      }
    })
  })
  bracketRounds.value
    .filter(round => round.type === 'preliminary')
    .forEach(round => {
      round.matches.forEach(match => {
        addRanking(rankings, seen, getMatchLoser(match), match.loserRank, match.loserScore)
      })
    })
  return rankings
})

const bracketTree = computed(() => {
  const boxW = 190
  const boxH = 40
  const slotGap = 10
  const matchHeight = boxH * 2 + slotGap
  const prelimStackGap = 12
  const xStep = 260
  const contentTop = 74
  const left = 22
  const rowGap = bracketMeta.value.playerCount > 24
    ? 28
    : bracketMeta.value.playerCount > 16
      ? 24
      : bracketMeta.value.playerCount > 8
        ? 20
        : 18
  const connectorOffset = 26
  const prelimRound = bracketRounds.value.find(round => round.type === 'preliminary')
  const rounds = mainRounds.value
  const roundPositions = []
  const playerNodes = []
  const lines = []
  const roundTitles = []
  let lineIndex = 0

  if (!rounds.length) {
    const champion = {
      x: left,
      y: contentTop,
      width: 150,
      height: 62
    }
    if (bracketChampion.value) {
      playerNodes.push({
        key: 'single-player',
        matchKey: 'single',
        roundIndex: 0,
        x: left,
        y: contentTop,
        width: boxW,
        height: boxH,
        player: bracketChampion.value,
        winner: true
      })
    }
    return {
      width: 420,
      height: 220,
      lines,
      playerNodes,
      roundTitles,
      champion,
      bronze: null
    }
  }

  const mainLeft = prelimRound ? left + xStep : left
  const prelimGroups = new Map()
  if (prelimRound) {
    prelimRound.matches.forEach((match) => {
      const targetMatchIndex = Math.floor(match.targetSlotIndex / 2)
      const group = prelimGroups.get(targetMatchIndex) || []
      group.push(match)
      prelimGroups.set(targetMatchIndex, group)
    })
  }
  const getPrelimGroupHeight = (count) => (
    count > 0 ? count * matchHeight + (count - 1) * prelimStackGap : 0
  )
  const firstRoundHalfHeights = (rounds[0]?.matches || []).map((_, matchIndex) => {
    const prelimHeight = getPrelimGroupHeight(prelimGroups.get(matchIndex)?.length || 0)
    return Math.max(matchHeight, prelimHeight) / 2
  })
  const firstRoundCenters = []
  firstRoundHalfHeights.forEach((halfHeight, matchIndex) => {
    if (matchIndex === 0) {
      firstRoundCenters[matchIndex] = contentTop + halfHeight
      return
    }
    firstRoundCenters[matchIndex] = firstRoundCenters[matchIndex - 1]
      + firstRoundHalfHeights[matchIndex - 1]
      + halfHeight
      + rowGap
  })

  rounds.forEach((round, roundColumnIndex) => {
    const x = mainLeft + roundColumnIndex * xStep
    roundTitles.push({
      key: `title-main-${roundColumnIndex}`,
      x,
      y: 26,
      title: round.title,
      subtitle: round.subtitle
    })

    roundPositions[roundColumnIndex] = []
    round.matches.forEach((match, matchIndex) => {
      const yCenter = roundColumnIndex === 0
        ? firstRoundCenters[matchIndex] || (contentTop + matchIndex * (matchHeight + rowGap) + matchHeight / 2)
        : (roundPositions[roundColumnIndex - 1][matchIndex * 2].yCenter + roundPositions[roundColumnIndex - 1][matchIndex * 2 + 1].yCenter) / 2
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
      roundPositions[roundColumnIndex][matchIndex] = position

      match.players.forEach((player, slotIndex) => {
        const slot = position.slots[slotIndex]
        playerNodes.push({
          key: `${match.key}-${slotIndex}`,
          matchKey: match.key,
          roundIndex: match.roundIndex,
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

  if (prelimRound) {
    const x = left
    const prelimCenters = new Map()
    prelimGroups.forEach((matches, targetMatchIndex) => {
      const targetPosition = roundPositions[0]?.[targetMatchIndex]
      if (!targetPosition) return
      const sortedMatches = matches.slice().sort((a, b) => a.targetSlotIndex - b.targetSlotIndex)
      let nextY = targetPosition.yCenter - getPrelimGroupHeight(sortedMatches.length) / 2
      sortedMatches.forEach((match) => {
        prelimCenters.set(match.key, nextY + matchHeight / 2)
        nextY += matchHeight + prelimStackGap
      })
    })
    roundTitles.push({
      key: 'title-preliminary',
      x,
      y: 26,
      title: prelimRound.title,
      subtitle: prelimRound.subtitle
    })
    prelimRound.matches.forEach((match) => {
      const targetMatchIndex = Math.floor(match.targetSlotIndex / 2)
      const targetSlotIndex = match.targetSlotIndex % 2
      const targetSlot = roundPositions[0]?.[targetMatchIndex]?.slots?.[targetSlotIndex]
      const yCenter = prelimCenters.get(match.key)
        || targetSlot?.yCenter
        || (contentTop + match.matchIndex * (matchHeight + rowGap) + matchHeight / 2)
      const firstY = yCenter - boxH - slotGap / 2
      const secondY = yCenter + slotGap / 2
      const outX = x + boxW + connectorOffset
      match.players.forEach((player, slotIndex) => {
        const y = slotIndex === 0 ? firstY : secondY
        playerNodes.push({
          key: `${match.key}-${slotIndex}`,
          matchKey: match.key,
          roundIndex: match.roundIndex,
          x,
          y,
          width: boxW,
          height: boxH,
          player,
          winner: match.winner?.id === player.id
        })
      })
      const y1 = firstY + boxH / 2
      const y2 = secondY + boxH / 2
      const mergeX = x + boxW + 12
      lines.push({
        key: `prelim-${lineIndex++}`,
        d: `M ${x + boxW} ${y1} H ${mergeX} V ${y2} H ${x + boxW} M ${mergeX} ${yCenter} H ${outX}`
      })
      if (targetSlot) {
        const midX = (outX + mainLeft) / 2
        lines.push({
          key: `prelim-target-${lineIndex++}`,
          d: `M ${outX} ${yCenter} H ${midX} V ${targetSlot.yCenter} H ${mainLeft}`
        })
      }
    })
  }

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
    const baseTreeHeight = playerNodes.reduce((max, node) => Math.max(max, node.y + node.height), 0)
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
        roundIndex: bronzeMatch.value.roundIndex,
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
      playerNodes.reduce((max, node) => Math.max(max, node.y + node.height), 0) + 56,
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

const formatCompetitionRule = () => '单淘汰'
const emitState = () => {
  emit('state-change', {
    drawSeed: drawSeed.value,
    winners: bracketWinners.value,
    rankings: bracketRankings.value,
    seedIds: seedMode.value === 'MANUAL' ? manualSeedIds.value : [],
    seedMode: seedMode.value
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
    if (key === 'bronze' && roundIndex < bracketRounds.value.length) {
      delete winnerState[key]
      return
    }
    const prelimRound = key.startsWith('p') ? 0 : null
    const mainRound = key.match(/^r(\d+)-/) ? Number(key.match(/^r(\d+)-/)[1]) + (bracketMeta.value.prelimMatchCount ? 1 : 0) : null
    const keyRound = prelimRound ?? mainRound
    if (keyRound !== null && keyRound > roundIndex) delete winnerState[key]
  })
}
const selectTreePlayer = (node) => {
  if (props.readonly || node.player.empty || node.player.bye || node.player.pending) return
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
  if (props.readonly || node.player.empty || node.player.bye || node.player.pending) return
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
  overflow: auto;
  max-height: min(78vh, 900px);
  padding: 12px;
  background: #f7faff;
  border: 1px solid #edf2f8;
  border-radius: 8px;
  box-sizing: border-box;
}
.tree-svg {
  min-width: 100%;
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
