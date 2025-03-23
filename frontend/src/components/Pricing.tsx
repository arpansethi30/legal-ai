import Link from 'next/link';

const pricingPlans = [
  {
    name: 'Basic',
    price: '$49',
    period: 'per month',
    description: 'Perfect for solo practitioners and small legal teams.',
    features: [
      'Document analysis (up to 100 pages/month)',
      'Basic contract review',
      'Limited legal research',
      'Email support',
      'Single user'
    ],
    cta: 'Get Started',
    highlight: false
  },
  {
    name: 'Professional',
    price: '$149',
    period: 'per month',
    description: 'Ideal for medium-sized firms with more document needs.',
    features: [
      'Document analysis (up to 1,000 pages/month)',
      'Advanced contract review',
      'Comprehensive legal research',
      'Clause library access',
      'Priority email support',
      'Up to 5 users'
    ],
    cta: 'Get Started',
    highlight: true
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: 'pricing',
    description: 'For large legal teams with advanced requirements.',
    features: [
      'Unlimited document analysis',
      'Custom AI training',
      'Integration with existing systems',
      'Dedicated account manager',
      '24/7 premium support',
      'Unlimited users'
    ],
    cta: 'Contact Sales',
    highlight: false
  }
];

const Pricing = () => {
  return (
    <section id="pricing" className="py-16 md:py-24 px-6 md:px-12 bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Choose the plan that fits your needs. All plans include a 14-day free trial.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {pricingPlans.map((plan, index) => (
            <div 
              key={index} 
              className={`bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden ${
                plan.highlight 
                  ? 'ring-2 ring-blue-500 dark:ring-blue-400 transform scale-105 md:-translate-y-2' 
                  : ''
              }`}
            >
              <div className={`p-8 ${
                plan.highlight 
                  ? 'bg-blue-600 dark:bg-blue-700' 
                  : 'bg-gray-100 dark:bg-gray-700'
              }`}>
                <h3 className={`text-xl font-bold mb-2 ${
                  plan.highlight 
                    ? 'text-white' 
                    : 'text-gray-900 dark:text-white'
                }`}>
                  {plan.name}
                </h3>
                <div className="flex items-baseline">
                  <span className={`text-4xl font-bold ${
                    plan.highlight 
                      ? 'text-white' 
                      : 'text-gray-900 dark:text-white'
                  }`}>
                    {plan.price}
                  </span>
                  <span className={`ml-2 ${
                    plan.highlight 
                      ? 'text-blue-100' 
                      : 'text-gray-500 dark:text-gray-300'
                  }`}>
                    {plan.period}
                  </span>
                </div>
                <p className={`mt-4 ${
                  plan.highlight 
                    ? 'text-blue-100' 
                    : 'text-gray-600 dark:text-gray-300'
                }`}>
                  {plan.description}
                </p>
              </div>
              
              <div className="p-8">
                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start">
                      <svg 
                        className="h-5 w-5 text-green-500 mt-0.5 mr-2" 
                        fill="none" 
                        viewBox="0 0 24 24" 
                        stroke="currentColor"
                      >
                        <path 
                          strokeLinecap="round" 
                          strokeLinejoin="round" 
                          strokeWidth={2} 
                          d="M5 13l4 4L19 7" 
                        />
                      </svg>
                      <span className="text-gray-600 dark:text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <Link 
                  href="/signup" 
                  className={`block w-full py-3 px-4 rounded-lg text-center font-medium ${
                    plan.highlight 
                      ? 'bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700 text-white'
                      : 'bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-12 text-center">
          <p className="text-gray-600 dark:text-gray-300">
            Need a custom solution? <Link href="/contact" className="text-blue-600 dark:text-blue-400 font-medium">Contact our sales team</Link>.
          </p>
        </div>
      </div>
    </section>
  );
};

export default Pricing; 