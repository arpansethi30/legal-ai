"use client";

import { motion } from "framer-motion";
import { Scale, Search, FileText, BookOpen, Database, Shield } from "lucide-react";

const features = [
  {
    title: "Legal Research Assistant",
    description: "Find relevant cases, statutes, and legal resources with AI-powered search",
    icon: Search,
  },
  {
    title: "Document Analysis",
    description: "Automatically review and analyze legal documents to extract key information",
    icon: FileText,
  },
  {
    title: "Case Law Insights",
    description: "Generate deep insights from case law to strengthen your legal arguments",
    icon: BookOpen,
  },
  {
    title: "Compliance Monitoring",
    description: "Stay updated on regulatory changes relevant to your practice areas",
    icon: Scale,
  },
  {
    title: "Knowledge Database",
    description: "Access a comprehensive database of legal precedents and information",
    icon: Database,
  },
  {
    title: "Data Security",
    description: "Enterprise-grade security to protect sensitive client information",
    icon: Shield,
  },
];

export function Features() {
  return (
    <section id="features" className="py-20 md:py-28">
      <div className="container mx-auto px-4 md:px-6">
        <div className="flex flex-col items-center justify-center text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
            Powerful Features for Legal Professionals
          </h2>
          <p className="mt-4 max-w-[700px] text-muted-foreground md:text-xl">
            Our suite of AI-powered tools is designed to streamline your legal workflow
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="flex flex-col p-6 bg-card rounded-lg border border-border hover:shadow-lg transition-all"
            >
              <div className="rounded-full p-3 w-12 h-12 bg-primary/10 mb-4">
                <feature.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
} 