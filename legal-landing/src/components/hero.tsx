"use client";

import { motion } from "framer-motion";
import { Button } from "./ui/button";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

export function Hero() {
  return (
    <section className="relative overflow-hidden py-20 md:py-32">
      {/* Background gradient */}
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(45%_40%_at_50%_60%,rgba(25,85,168,0.08),transparent)]" />

      <div className="container mx-auto px-4 md:px-6">
        <div className="flex flex-col items-center justify-center space-y-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-block rounded-full bg-primary/10 px-3 py-1 text-sm text-primary"
          >
            Revolutionizing Legal Research
          </motion.div>

          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl max-w-3xl"
          >
            AI-Powered Legal Analysis for the Modern Attorney
          </motion.h1>

          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="max-w-[700px] text-muted-foreground md:text-xl"
          >
            Simplify complex legal research, automate document review, and generate insights from case law with our advanced AI platform.
          </motion.p>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-4"
          >
            <Button size="lg" className="h-12 px-8">Get Started</Button>
            <Link 
              href="#how-it-works" 
              className="flex items-center gap-1 text-primary hover:underline"
            >
              See how it works <ArrowRight className="h-4 w-4" />
            </Link>
          </motion.div>
        </div>
      </div>

      {/* Stats */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="container mx-auto mt-16 md:mt-24 px-4 md:px-6"
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 border-t border-border pt-8">
          <div className="flex flex-col">
            <span className="text-3xl font-bold">99%</span>
            <span className="text-muted-foreground">Accuracy Rate</span>
          </div>
          <div className="flex flex-col">
            <span className="text-3xl font-bold">85%</span>
            <span className="text-muted-foreground">Time Saved</span>
          </div>
          <div className="flex flex-col">
            <span className="text-3xl font-bold">10k+</span>
            <span className="text-muted-foreground">Legal Professionals</span>
          </div>
          <div className="flex flex-col">
            <span className="text-3xl font-bold">500k+</span>
            <span className="text-muted-foreground">Documents Processed</span>
          </div>
        </div>
      </motion.div>
    </section>
  );
} 