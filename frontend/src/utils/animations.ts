/**
 * Framer Motion animation variants
 */

export const voiceBubbleVariants = {
  idle: {
    scale: 1,
    opacity: 0.8,
    boxShadow: '0 0 20px rgba(159, 122, 255, 0.3)',
  },
  listening: {
    scale: [1, 1.08, 1.05, 1.1, 1],
    opacity: 1,
    boxShadow: '0 0 40px rgba(159, 122, 255, 0.6)',
    transition: {
      scale: { duration: 0.4, repeat: Infinity, repeatType: 'loop' as const },
      opacity: { duration: 0.3 },
      boxShadow: { duration: 0.3 },
    },
  },
  thinking: {
    scale: 1,
    opacity: 0.9,
    boxShadow: '0 0 30px rgba(159, 122, 255, 0.5)',
    transition: {
      opacity: { duration: 0.2 },
      boxShadow: { duration: 0.2 },
    },
  },
  speaking: {
    scale: [1, 1.05, 0.98, 1.03, 1],
    opacity: 1,
    boxShadow: '0 0 50px rgba(159, 122, 255, 0.7)',
    transition: {
      scale: { duration: 0.5, repeat: Infinity, repeatType: 'loop' as const },
      opacity: { duration: 0.3 },
      boxShadow: { duration: 0.3 },
    },
  },
  error: {
    scale: 0.95,
    opacity: 1,
    boxShadow: '0 0 40px rgba(239, 68, 68, 0.6)',
    transition: {
      duration: 0.3,
    },
  },
};

export const innerCircleVariants = {
  idle: {
    scale: 0.5,
    opacity: 0.5,
  },
  listening: {
    scale: [0.6, 0.8, 0.65],
    opacity: [0.6, 1, 0.6],
    transition: {
      duration: 0.4,
      repeat: Infinity,
      repeatType: 'loop' as const,
    },
  },
  thinking: {
    scale: 0.7,
    opacity: 0.8,
    rotate: 360,
    transition: {
      rotate: { duration: 2, repeat: Infinity, repeatType: 'loop' as const },
      scale: { duration: 0.2 },
      opacity: { duration: 0.2 },
    },
  },
  speaking: {
    scale: [0.5, 0.9, 0.55, 0.85, 0.5],
    opacity: [0.7, 1, 0.7, 1, 0.7],
    transition: {
      duration: 0.6,
      repeat: Infinity,
      repeatType: 'loop' as const,
    },
  },
  error: {
    scale: 0.5,
    opacity: 1,
    rotate: 0,
    transition: {
      duration: 0.3,
    },
  },
};

export const transcriptVariants = {
  initial: {
    opacity: 0,
    y: 10,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
    },
  },
  exit: {
    opacity: 0,
    y: -10,
    transition: {
      duration: 0.2,
    },
  },
};

export const containerVariants = {
  initial: { opacity: 0 },
  animate: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
    },
  },
};

export const itemVariants = {
  initial: { opacity: 0, x: -20 },
  animate: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.3 },
  },
};
