"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

const faqs = [
  {
    question: "How does LegalAI help with legal research?",
    answer: "LegalAI uses advanced natural language processing to understand your legal queries, search through millions of legal documents, and return the most relevant cases, statutes, and legal resources for your needs."
  },
  {
    question: "Is my data secure with LegalAI?",
    answer: "Yes, we take data security seriously. All documents and information are encrypted, and we comply with the highest security standards. We never share your data with third parties without explicit consent."
  },
  {
    question: "Can LegalAI handle different practice areas?",
    answer: "Absolutely. LegalAI is trained on diverse legal content covering various practice areas including corporate law, intellectual property, family law, criminal law, and more."
  },
  {
    question: "Do I need technical expertise to use LegalAI?",
    answer: "Not at all. LegalAI is designed with an intuitive interface that requires no technical expertise. You can interact with it using natural language, just as you would ask a question to a colleague."
  },
  {
    question: "How accurate is LegalAI?",
    answer: "LegalAI maintains a high accuracy rate, with continuous improvements based on feedback from legal professionals. While it's an excellent research assistant, we always recommend human review for critical legal work."
  },
  {
    question: "How much does LegalAI cost?",
    answer: "LegalAI offers flexible pricing plans to suit different needs, from solo practitioners to large law firms. We offer a free trial period so you can experience the benefits before committing."
  }
];

export function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleFaq = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section id="faq" className="py-20 md:py-28">
      <div className="container mx-auto px-4 md:px-6">
        <div className="flex flex-col items-center justify-center text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
            Frequently Asked Questions
          </h2>
          <p className="mt-4 max-w-[700px] text-muted-foreground md:text-xl">
            Have questions about how LegalAI can help your practice? We've got answers.
          </p>
        </div>

        <div className="max-w-3xl mx-auto">
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <motion.div 
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="border border-border rounded-lg overflow-hidden"
              >
                <button
                  onClick={() => toggleFaq(index)}
                  className="flex justify-between items-center w-full p-6 text-left"
                >
                  <h3 className="text-lg font-medium">{faq.question}</h3>
                  <ChevronDown 
                    className={cn(
                      "h-5 w-5 transition-transform",
                      openIndex === index ? "transform rotate-180" : ""
                    )} 
                  />
                </button>
                <div 
                  className={cn(
                    "overflow-hidden transition-all duration-300",
                    openIndex === index ? "max-h-96 p-6 pt-0" : "max-h-0"
                  )}
                >
                  <p className="text-muted-foreground">{faq.answer}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
} 