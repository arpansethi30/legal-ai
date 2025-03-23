import Image from 'next/image';

const testimonials = [
  {
    quote: "LegalAI has transformed how our firm handles document review. What used to take days now takes hours.",
    author: "Sarah Johnson",
    title: "Partner, Johnson & Associates",
    avatar: "/avatars/sarah.jpg",
  },
  {
    quote: "The contract analysis feature has helped us identify critical issues that we might have otherwise missed.",
    author: "Michael Chen",
    title: "Legal Counsel, TechCorp Inc.",
    avatar: "/avatars/michael.jpg",
  },
  {
    quote: "As a solo practitioner, LegalAI gives me the capabilities of a large firm at a fraction of the cost.",
    author: "Emily Rodriguez",
    title: "Independent Attorney",
    avatar: "/avatars/emily.jpg",
  },
];

const Testimonials = () => {
  return (
    <section id="testimonials" className="py-16 md:py-24 px-6 md:px-12">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Trusted by Legal Professionals
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            See what our clients say about how LegalAI has improved their workflow.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <div 
              key={index} 
              className="bg-white dark:bg-gray-800 p-8 rounded-xl shadow-md border border-gray-100 dark:border-gray-700"
            >
              <div className="flex mb-6">
                {[...Array(5)].map((_, i) => (
                  <svg 
                    key={i} 
                    className="w-5 h-5 text-yellow-400" 
                    fill="currentColor" 
                    viewBox="0 0 20 20"
                  >
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                ))}
              </div>
              
              <blockquote className="text-gray-600 dark:text-gray-300 mb-6 italic">
                "{testimonial.quote}"
              </blockquote>
              
              <div className="flex items-center">
                <div className="w-12 h-12 relative mr-4">
                  <Image 
                    src={testimonial.avatar} 
                    alt={testimonial.author}
                    fill
                    className="rounded-full object-cover"
                  />
                </div>
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">{testimonial.author}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{testimonial.title}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Testimonials; 