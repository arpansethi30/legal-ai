"use client";

import { motion } from "framer-motion";

const steps = [
  {
    number: "01",
    title: "Sign Up for an Account",
    description: "Create your account in minutes and get access to all of our powerful features.",
  },
  {
    number: "02",
    title: "Upload Your Documents",
    description: "Securely upload legal documents for AI analysis and extraction of key information.",
  },
  {
    number: "03",
    title: "Ask Legal Questions",
    description: "Use natural language to query about legal concepts, statutes, or specific cases.",
  },
  {
    number: "04",
    title: "Review AI-Generated Insights",
    description: "Get instant insights, summaries, and relevant citations for your legal work.",
  },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="py-20 md:py-28 bg-secondary/50">
      <div className="container mx-auto px-4 md:px-6">
        <div className="flex flex-col items-center justify-center text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
            How LegalAI Works
          </h2>
          <p className="mt-4 max-w-[700px] text-muted-foreground md:text-xl">
            Our platform is designed to be intuitive and easy to use, saving you time and effort
          </p>
        </div>

        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-1/2 h-full w-0.5 bg-border transform -translate-x-1/2 hidden md:block" />
          
          <div className="space-y-24">
            {steps.map((step, index) => (
              <motion.div
                key={step.number}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className={`flex flex-col ${index % 2 === 0 ? 'md:flex-row' : 'md:flex-row-reverse'} gap-8 md:gap-16 items-center`}
              >
                <div className="w-full md:w-1/2 flex flex-col items-center md:items-start text-center md:text-left">
                  <div className="text-primary font-bold text-4xl mb-3">{step.number}</div>
                  <h3 className="text-2xl font-bold mb-2">{step.title}</h3>
                  <p className="text-muted-foreground">{step.description}</p>
                </div>
                <div className="w-full md:w-1/2 h-64 bg-card rounded-lg border border-border flex items-center justify-center relative">
                  <div className="absolute -z-10 inset-0 bg-[radial-gradient(40%_40%_at_50%_50%,rgba(25,85,168,0.06),transparent)] rounded-lg" />
                  <div className="text-primary/30 text-8xl font-bold">{step.number}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
} 