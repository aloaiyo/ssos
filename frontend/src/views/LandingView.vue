<template>
  <div class="landing-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-overlay"></div>
      <v-container class="hero-content">
        <v-row align="center" justify="center" class="fill-height">
          <v-col cols="12" md="8" lg="6" class="text-center">
            <div class="hero-badge animate-fade-in">
              <v-chip color="white" variant="outlined" size="small">
                <v-icon start size="small">mdi-tennis</v-icon>
                테니스 동호회 관리의 새로운 기준
              </v-chip>
            </div>
            <h1 class="hero-title animate-slide-up">
              스마트하게 관리하는<br />
              <span class="text-accent">테니스 동호회</span>
            </h1>
            <p class="hero-subtitle animate-slide-up-delay">
              자동 매칭부터 랭킹 관리까지,<br />
              동호회 운영의 모든 것을 한 곳에서
            </p>
            <div class="hero-actions animate-fade-in-delay">
              <v-btn
                size="x-large"
                color="white"
                class="mr-4 text-primary font-weight-bold"
                rounded="pill"
                :to="{ name: 'register' }"
              >
                <v-icon start>mdi-account-plus</v-icon>
                무료로 시작하기
              </v-btn>
              <v-btn
                size="x-large"
                variant="outlined"
                color="white"
                rounded="pill"
                :to="{ name: 'login' }"
              >
                로그인
              </v-btn>
            </div>
          </v-col>
        </v-row>
      </v-container>
      <!-- Floating Tennis Balls -->
      <div class="floating-balls">
        <div class="ball ball-1"></div>
        <div class="ball ball-2"></div>
        <div class="ball ball-3"></div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <v-container>
        <div class="section-header text-center mb-12">
          <h2 class="section-title">주요 기능</h2>
          <p class="section-subtitle">
            동호회 운영에 필요한 모든 기능을 제공합니다
          </p>
        </div>
        <v-row>
          <v-col
            v-for="(feature, index) in features"
            :key="index"
            cols="12"
            md="6"
            lg="3"
          >
            <v-card
              class="feature-card h-100"
              variant="outlined"
              :style="{ animationDelay: `${index * 0.1}s` }"
            >
              <v-card-text class="text-center pa-6">
                <div class="feature-icon-wrapper mb-4">
                  <v-icon :icon="feature.icon" size="48" color="primary" />
                </div>
                <h3 class="feature-title mb-2">{{ feature.title }}</h3>
                <p class="feature-description text-medium-emphasis">
                  {{ feature.description }}
                </p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- How It Works Section -->
    <section class="how-it-works-section">
      <v-container>
        <div class="section-header text-center mb-12">
          <h2 class="section-title">이용 방법</h2>
          <p class="section-subtitle">3단계로 간편하게 시작하세요</p>
        </div>
        <v-row justify="center">
          <v-col
            v-for="(step, index) in steps"
            :key="index"
            cols="12"
            md="4"
            class="step-col"
          >
            <div class="step-card text-center">
              <div class="step-number">{{ index + 1 }}</div>
              <div class="step-icon-wrapper">
                <v-icon :icon="step.icon" size="40" color="primary" />
              </div>
              <h3 class="step-title">{{ step.title }}</h3>
              <p class="step-description text-medium-emphasis">
                {{ step.description }}
              </p>
            </div>
            <div v-if="index < steps.length - 1" class="step-connector d-none d-md-block">
              <v-icon icon="mdi-chevron-right" size="32" color="primary" />
            </div>
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- Stats Section -->
    <section class="stats-section">
      <v-container>
        <v-row>
          <v-col
            v-for="(stat, index) in stats"
            :key="index"
            cols="6"
            md="3"
            class="text-center"
          >
            <div class="stat-number">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <v-container>
        <v-row align="center" justify="center">
          <v-col cols="12" md="8" class="text-center">
            <h2 class="cta-title">지금 바로 시작하세요</h2>
            <p class="cta-subtitle mb-8">
              무료 회원으로 시작하여 동호회 1개를 관리할 수 있습니다.<br />
              프리미엄으로 업그레이드하면 최대 10개까지 확장 가능!
            </p>
            <v-btn
              size="x-large"
              color="white"
              class="text-primary font-weight-bold"
              rounded="pill"
              :to="{ name: 'register' }"
            >
              <v-icon start>mdi-rocket-launch</v-icon>
              무료로 시작하기
            </v-btn>
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- Footer -->
    <footer class="landing-footer">
      <v-container>
        <v-row align="center">
          <v-col cols="12" md="6" class="text-center text-md-start">
            <div class="footer-logo">
              <v-icon icon="mdi-tennis" size="24" class="mr-2" />
              테니스 동호회 관리
            </div>
          </v-col>
          <v-col cols="12" md="6" class="text-center text-md-end">
            <span class="footer-copyright">
              &copy; {{ currentYear }} Tennis Club Manager. All rights reserved.
            </span>
          </v-col>
        </v-row>
      </v-container>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const currentYear = computed(() => new Date().getFullYear())

const features = [
  {
    icon: 'mdi-account-group',
    title: '회원 관리',
    description: '회원 정보, 출석, 회비 납부 현황을 체계적으로 관리합니다.',
  },
  {
    icon: 'mdi-shuffle-variant',
    title: '자동 매칭',
    description: '성별, 실력을 고려한 공정한 게임 매칭을 자동으로 생성합니다.',
  },
  {
    icon: 'mdi-trophy',
    title: '랭킹 시스템',
    description: '경기 결과를 기반으로 실시간 랭킹을 자동 산출합니다.',
  },
  {
    icon: 'mdi-calendar-check',
    title: '일정 관리',
    description: '정기 모임, 이벤트 일정을 손쉽게 관리하고 공유합니다.',
  },
]

const steps = [
  {
    icon: 'mdi-account-plus',
    title: '회원가입',
    description: '이메일로 간편하게 가입하세요',
  },
  {
    icon: 'mdi-tennis-ball',
    title: '동호회 생성',
    description: '나만의 동호회를 만들어보세요',
  },
  {
    icon: 'mdi-play-circle',
    title: '게임 시작',
    description: '자동 매칭으로 게임을 즐기세요',
  },
]

const stats = [
  { value: '500+', label: '등록 동호회' },
  { value: '10,000+', label: '활동 회원' },
  { value: '50,000+', label: '진행 게임' },
  { value: '99%', label: '만족도' },
]
</script>

<style scoped>
/* Hero Section */
.hero-section {
  position: relative;
  min-height: 100vh;
  background: linear-gradient(135deg, #059669 0%, #10B981 50%, #34D399 100%);
  display: flex;
  align-items: center;
  overflow: hidden;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.hero-content {
  position: relative;
  z-index: 2;
}

.hero-badge {
  margin-bottom: 24px;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  color: white;
  line-height: 1.2;
  margin-bottom: 24px;
}

.hero-title .text-accent {
  color: #6EE7B7;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.8;
  margin-bottom: 40px;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

/* Floating Tennis Balls */
.floating-balls {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.ball {
  position: absolute;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #C5E1A5 0%, #9CCC65 100%);
  opacity: 0.3;
}

.ball-1 {
  top: 20%;
  left: 10%;
  animation: float 6s ease-in-out infinite;
}

.ball-2 {
  top: 60%;
  right: 15%;
  width: 40px;
  height: 40px;
  animation: float 8s ease-in-out infinite reverse;
}

.ball-3 {
  bottom: 20%;
  left: 20%;
  width: 80px;
  height: 80px;
  animation: float 7s ease-in-out infinite;
  animation-delay: 1s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-30px) rotate(180deg);
  }
}

/* Features Section */
.features-section {
  padding: 100px 0;
  background: #FAFAFA;
}

.section-header {
  margin-bottom: 60px;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #059669;
  margin-bottom: 16px;
}

.section-subtitle {
  font-size: 1.125rem;
  color: #666;
}

.feature-card {
  border-radius: 16px !important;
  transition: all 0.3s ease;
  border-color: #D1FAE5 !important;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(16, 185, 129, 0.15) !important;
  border-color: #10B981 !important;
}

.feature-icon-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.feature-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #059669;
}

.feature-description {
  font-size: 0.95rem;
  line-height: 1.6;
}

/* How It Works Section */
.how-it-works-section {
  padding: 100px 0;
  background: white;
}

.step-col {
  position: relative;
}

.step-card {
  padding: 32px;
}

.step-number {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #059669 0%, #10B981 100%);
  color: white;
  font-size: 1.5rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
}

.step-icon-wrapper {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: #D1FAE5;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
}

.step-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #059669;
  margin-bottom: 8px;
}

.step-description {
  font-size: 0.95rem;
}

.step-connector {
  position: absolute;
  top: 50%;
  right: -16px;
  transform: translateY(-50%);
}

/* Stats Section */
.stats-section {
  padding: 80px 0;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
}

.stat-number {
  font-size: 3rem;
  font-weight: 800;
  color: white;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
}

/* CTA Section */
.cta-section {
  padding: 100px 0;
  background: linear-gradient(135deg, #10B981 0%, #34D399 100%);
}

.cta-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 16px;
}

.cta-subtitle {
  font-size: 1.125rem;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.8;
}

/* Footer */
.landing-footer {
  padding: 32px 0;
  background: #065F46;
}

.footer-logo {
  font-size: 1.125rem;
  font-weight: 600;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (min-width: 960px) {
  .footer-logo {
    justify-content: flex-start;
  }
}

.footer-copyright {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.875rem;
}

/* Animations */
.animate-fade-in {
  animation: fadeIn 0.8s ease-out;
}

.animate-fade-in-delay {
  animation: fadeIn 0.8s ease-out 0.4s both;
}

.animate-slide-up {
  animation: slideUp 0.8s ease-out;
}

.animate-slide-up-delay {
  animation: slideUp 0.8s ease-out 0.2s both;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 960px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .section-title {
    font-size: 2rem;
  }

  .stat-number {
    font-size: 2rem;
  }

  .cta-title {
    font-size: 2rem;
  }
}

@media (max-width: 600px) {
  .hero-title {
    font-size: 2rem;
  }

  .hero-actions {
    flex-direction: column;
    align-items: center;
  }

  .hero-actions .v-btn {
    width: 100%;
    max-width: 280px;
    margin-right: 0 !important;
    margin-bottom: 12px;
  }
}
</style>
