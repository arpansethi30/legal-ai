"use client";

import { motion } from "framer-motion";
import { Button } from "./ui/button";

export function CTA() {
  return (
    <section className="py-20 md:py-28">
      <div className="container mx-auto px-4 md:px-6">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
          className="relative rounded-3xl overflow-hidden bg-primary px-6 py-16 sm:px-12 md:p-16 lg:p-20"
        >
          {/* Background pattern */}
          <div className="absolute inset-0 -z-10 bg-[linear-gradient(to_right,rgba(25,85,168,0.9),rgba(25,85,168,1))]" />
          <div className="absolute inset-0 -z-10 bg-[radial-gradient(75%_40%_at_50%_60%,rgba(255,255,255,0.1),transparent)]" />
          
          <div className="flex flex-col items-center text-center">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-white max-w-2xl">
              Transform Your Legal Practice with AI Today
            </h2>
            <p className="mt-4 max-w-[800px] text-primary-foreground/80 md:text-xl">
              Join thousands of legal professionals already using LegalAI to save time, reduce costs, and deliver better results for their clients.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row gap-4">
              <Button size="lg" className="bg-white text-primary hover:bg-white/90 h-12 px-8">
                Get Started for Free
              </Button>
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10 h-12 px-8">
                Request a Demo
              </Button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
} 